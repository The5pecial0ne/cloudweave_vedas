# Cloudweave Runner/RIFE-Cloudweave-main/get_wms_img_updated.py

import os
import sys
import subprocess
import tempfile
import requests
import mercantile
from datetime import datetime, timedelta
from pyproj import Transformer
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests.adapters import HTTPAdapter, Retry
from PIL import Image
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# ——— CONFIG ——————————————————————————————————————————————
BASE_URL = (
    "https://mosdac.gov.in/live_data/wms/"
    "live3RL1BSTD1km/products/Insat3r/3R_IMG/"
)
WMS_PARAMS = {
    "SERVICE": "WMS",
    "VERSION": "1.3.0",
    "REQUEST": "GetMap",
    "FORMAT": "image/png",
    "TRANSPARENT": "true",
    "LAYERS": "IMG_VIS",
    "STYLES": "boxfill/greyscale",
    "COLORSCALERANGE": "0,407",
    "BELOWMINCOLOR": "extend",
    "ABOVEMAXCOLOR": "extend",
    "CRS": "EPSG:3857",
    "WIDTH": "256",
    "HEIGHT": "256",
}
# Coordinate transformers
proj_to_merc = Transformer.from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
proj_to_wgs  = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)

class InterpRequest(BaseModel):
    lon_min:     float
    lat_min:     float
    lon_max:     float
    lat_max:     float
    start_iso:   datetime
    end_iso:     datetime
    zoom:        int = 7
    max_workers: int = 8

app = FastAPI()


def project_bbox(lon_min, lat_min, lon_max, lat_max):
    x0, y0 = proj_to_merc.transform(lon_min, lat_min)
    x1, y1 = proj_to_merc.transform(lon_max, lat_max)
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def tiles_for_bbox(bbox, zoom):
    xmin, ymin, xmax, ymax = bbox
    lon_min, lat_min = proj_to_wgs.transform(xmin, ymin)
    lon_max, lat_max = proj_to_wgs.transform(xmax, ymax)
    ul = mercantile.tile(lon_min, lat_max, zoom)
    lr = mercantile.tile(lon_max, lat_min, zoom)
    return [mercantile.Tile(x, y, zoom)
            for x in range(ul.x, lr.x + 1)
            for y in range(ul.y, lr.y + 1)]


def build_tile_request(tile, timestamp):
    path = timestamp.strftime("%Y/%d%b/3RIMG_%d%b%Y_%H%M_L1B_STD_V01R00.h5")
    url = BASE_URL + path
    b = mercantile.xy_bounds(tile)
    params = WMS_PARAMS.copy()
    params["BBOX"] = f"{b.left},{b.bottom},{b.right},{b.top}"
    return url, params


def create_session_with_retries(total_retries=3, backoff=0.3):
    session = requests.Session()
    retry = Retry(
        total=total_retries,
        backoff_factor=backoff,
        status_forcelist=[500,502,503,504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def process_pipeline(lon_min, lat_min, lon_max, lat_max,
                     start_dt, end_dt, zoom, max_workers):
    session = create_session_with_retries()
    bbox    = project_bbox(lon_min, lat_min, lon_max, lat_max)
    tiles   = tiles_for_bbox(bbox, zoom)

    # locate inference script
    SCRIPT_DIR       = Path(__file__).parent
    inference_script = SCRIPT_DIR / "inference_video.py"

    # calculate total steps
    periods     = ((end_dt - start_dt).seconds // 1800) + 1
    total_steps = periods * 2 + 1
    step        = 0

    with tempfile.TemporaryDirectory() as tmpdir:
        base_dir   = Path(tmpdir)
        tiles_dir  = base_dir / "tiles"
        stitch_dir = base_dir / "stitched"
        tiles_dir.mkdir()
        stitch_dir.mkdir()

        current = start_dt
        while current <= end_dt:
            ts = current.strftime("%Y%m%d_%H%M")
            frame_dir = tiles_dir / ts
            frame_dir.mkdir(exist_ok=True)

            # parallel downloads
            with ThreadPoolExecutor(max_workers=max_workers) as ex:
                futures = {ex.submit(session.get, *build_tile_request(t, current), timeout=30): t for t in tiles}
                for fut in as_completed(futures):
                    t = futures[fut]
                    try:
                        r = fut.result(); r.raise_for_status()
                        (frame_dir / f"{t.x}_{t.y}.png").write_bytes(r.content)
                    except:
                        pass

            # stitch mosaic
            xs = sorted({t.x for t in tiles}); ys = sorted({t.y for t in tiles})
            mosaic = Image.new("RGB", (256 * len(xs), 256 * len(ys)))
            for i, x in enumerate(xs):
                for j, y in enumerate(ys):
                    p = frame_dir / f"{x}_{y}.png"
                    if p.exists(): mosaic.paste(Image.open(p), (i*256, j*256))
            out_img = stitch_dir / f"{ts}.png"
            mosaic.save(out_img)

            # send progress
            step += 2
            pct  = int(step / total_steps * 100)
            yield f"data: {{\"progress\":{pct},\"message\":\"stitched {ts}\"}}\n\n"

            current += timedelta(minutes=30)

        # write output video to backend/videos
        video_out = Path(__file__).parents[2] / "backend" / "videos" / "output.mp4"
        video_out.parent.mkdir(parents=True, exist_ok=True)

        # run inference
        subprocess.run([
            sys.executable,
            str(inference_script),
            "--img", str(stitch_dir),
            "--output", str(video_out),
            "--model", str(SCRIPT_DIR / "train_log")
        ], check=True, cwd=str(SCRIPT_DIR))

        # also copy to frontend root so /output.mp4 works
        FRONTEND_DIR = Path(__file__).parents[2] / "frontend"
        FRONTEND_DIR.mkdir(parents=True, exist_ok=True)
        (FRONTEND_DIR / video_out.name).write_bytes(video_out.read_bytes())

        # final SSE with root path
        yield f"data: {{\"progress\":100,\"message\":\"done\",\"video_url\":\"/{video_out.name}\"}}\n\n"

# JSON POST → SSE
@app.post("/interpolate/stream")
async def _stream_post(req: InterpRequest):
    try:
        return StreamingResponse(
            process_pipeline(
                req.lon_min, req.lat_min,
                req.lon_max, req.lat_max,
                req.start_iso, req.end_iso,
                req.zoom, req.max_workers
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))

# SSE GET → SSE
@app.get("/interpolate/stream")
async def stream_get(
    lon_min:     float    = Query(...),
    lat_min:     float    = Query(...),
    lon_max:     float    = Query(...),
    lat_max:     float    = Query(...),
    start_iso:   datetime = Query(...),
    end_iso:     datetime = Query(...),
    zoom:        int      = Query(7),
    max_workers: int      = Query(8),
):
    try:
        return StreamingResponse(
            process_pipeline(
                lon_min, lat_min,
                lon_max, lat_max,
                start_iso, end_iso,
                zoom, max_workers
            ),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(500, detail=str(e))
