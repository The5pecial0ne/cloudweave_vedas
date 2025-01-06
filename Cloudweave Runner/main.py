import os
import subprocess
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
import uuid
import time
from pyproj import Transformer

app = FastAPI()


# CORS middleware
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files server
app.mount("/static", StaticFiles(directory="static"), name="static")

class InterpolationParams(BaseModel):
    bbox: str
    width: int
    height: int
    start_time: str
    end_time: str

    # Optional parameters based on the script's argument parser
    exp: int = 4
    scale: float = 1.0
    fps: Optional[int] = None
    png: bool = False
    ext: str = 'mp4'

transformer = Transformer.from_crs("EPSG:4326","EPSG:3857")

@app.get("/")
async def main():
    return {"message": "Hello World"}

@app.post("/interpolate")
async def interpolate_video(params: InterpolationParams):
    try:
        # Validate input parameters
        try:
            start_time = datetime.fromisoformat(params.start_time.replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(params.end_time.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid datetime format")

        # Get the directory of the current script
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the RIFE-Cloudweave folder
        rife_dir = os.path.join(current_dir, 'RIFE-Cloudweave')

        # Ensure input_frames and vid_out directories exist and are clean
        input_frames_dir = os.path.join(rife_dir, 'input_frames')
        vid_out_dir = os.path.join(rife_dir, 'vid_out')

        # Clean existing directories
        for dir_path in [input_frames_dir, vid_out_dir]:
            if os.path.exists(dir_path):
                # Remove all files in the directory
                for filename in os.listdir(dir_path):
                    file_path = os.path.join(dir_path, filename)
                    try:
                        if os.path.isfile(file_path) or os.path.islink(file_path):
                            os.unlink(file_path)
                        elif os.path.isdir(file_path):
                            import shutil
                            shutil.rmtree(file_path)
                    except Exception as e:
                        print(f"Failed to delete {file_path}. Reason: {e}")
            else:
                # Create the directory if it doesn't exist
                os.makedirs(dir_path)

        # Create a unique output folder in the root directory
        unique_id = str(uuid.uuid4())
        output_folder = os.path.join('static', f'interpolated_videos_{unique_id}')
        os.makedirs(output_folder, exist_ok=True)

        # Construct command arguments
        cmd_args = [
            'python', 'inference_video.py',
            '--img', 'input_frames/',
            '--bbox', params.bbox,
            '--width', str(params.width),
            '--height', str(params.height),
            '--start_time', params.start_time,
            '--end_time', params.end_time,
            '--exp', str(params.exp),
            '--scale', str(params.scale),
            '--ext', params.ext,
        ]

        # Optional parameters
        if params.fps is not None:
            cmd_args.extend(['--fps', str(params.fps)])
        if params.png:
            cmd_args.append('--png')

        # Run the interpolation from the RIFE-Cloudweave directory
        print("Starting interpolation process...")
        start_time = time.time()

        result = subprocess.run(
            cmd_args,
            cwd=rife_dir,  # Set working directory to RIFE-Cloudweave
            capture_output=True,  # Capture output
            timeout=1200,  # 20 minutes timeout
            text=True
        )

        end_time = time.time()
        print(f"Interpolation process completed in {end_time - start_time:.2f} seconds")

        # Check for errors
        if result.returncode != 0:
            print("Stderr:", result.stderr)
            raise HTTPException(status_code=500, detail=f"Interpolation failed: {result.stderr}")

        # Find the output frames
        output_frames = sorted([f for f in os.listdir(vid_out_dir) if f.endswith('.png')])

        if not output_frames:
            raise HTTPException(status_code=404, detail="No output frames found")

        # Prepare FFmpeg command to compile frames into video
        output_video_path = os.path.join(output_folder, f'interpolated_{unique_id}.mp4')

        # Determine FPS (use default 5 if not specified)
        fps = params.fps if params.fps is not None else 24

        # FFmpeg command to convert frames to video
        ffmpeg_cmd = [
            'ffmpeg',
            '-framerate', str(fps),
            '-i', os.path.join(vid_out_dir, '%07d.png'),
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-vf', "scale=ceil(iw/2)*2:ceil(ih/2)*2,lut=a='if(val<50,0,255)'",
            output_video_path
        ]

        # Run FFmpeg
        print("Starting video compilation...")
        ffmpeg_start_time = time.time()
        ffmpeg_result = subprocess.run(
            ffmpeg_cmd,
            capture_output=True,
            text=True
        )
        ffmpeg_end_time = time.time()
        print(f"Video compilation completed in {ffmpeg_end_time - ffmpeg_start_time:.2f} seconds")

        # Check FFmpeg result
        if ffmpeg_result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"Video compilation failed: {ffmpeg_result.stderr}")

        # Create HLS stream
        hls_output_dir = os.path.join(output_folder, 'hls')
        os.makedirs(hls_output_dir, exist_ok=True)

        # HLS conversion command
        hls_cmd = [
            'ffmpeg',
            '-i', output_video_path,
            '-start_number', '0',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-f', 'hls',
            '-vf', "scale=ceil(iw/2)*2:ceil(ih/2)*2,lut=a='if(val<50,0,255)'",
            os.path.join(hls_output_dir, 'output.m3u8')
        ]

        # Run HLS conversion
        print("Starting HLS conversion...")
        hls_start_time = time.time()
        hls_result = subprocess.run(
            hls_cmd,
            capture_output=True,
            text=True
        )
        hls_end_time = time.time()
        print(f"HLS conversion completed in {hls_end_time - hls_start_time:.2f} seconds")

        # Check HLS conversion result
        if hls_result.returncode != 0:
            raise HTTPException(status_code=500, detail=f"HLS conversion failed: {hls_result.stderr}")

        return {
            "status": "success",
            "output_video": f'/static/interpolated_videos_{unique_id}/interpolated_{unique_id}.mp4',
            "output_frames_directory": vid_out_dir,
            "hls_playlist": f'/static/interpolated_videos_{unique_id}/hls/output.m3u8',
            "hls_directory": f'/static/interpolated_videos_{unique_id}/hls',
            "unique_id": unique_id,
            "num_output_frames": len(output_frames)
        }

    except Exception as e:
        print(f"Error in interpolation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}
