import { useEffect, useState } from "react";
import {
  MapContainer,
  SVGOverlay,
  TileLayer,
  VideoOverlay,
} from "react-leaflet";
import SelectArea from "@/components/select-area";
import { Map, VideoOverlay as LeafletVideoOverlay } from "leaflet";
import Hls from "hls.js";
import Loader from "./loader";

export default function MainMap({
  onLngChange,
  onLatChange,
  onZoomChange,
}: {
  onLngChange?: (lng: string) => void;
  onLatChange?: (lat: string) => void;
  onZoomChange?: (zoom: number) => void;
}) {
  const [map, setMap] = useState<Map | null>(null);

  const [videoRef, setVideoRef] = useState<LeafletVideoOverlay | null>(null);
  const [videoLoading, setVideoLoading] = useState(false);

  const [selectedArea, setSelectedArea] = useState<
    [[number, number], [number, number]] | null
  >(null);

  useEffect(() => {
    if (map) {
      map.on("move", () => {
        onLngChange && onLngChange(map.getCenter().lat.toFixed(4));
        onLatChange && onLatChange(map.getCenter().lng.toFixed(4));
        onZoomChange && onZoomChange(map.getZoom());
      });
    }
  }, [map]);

  useEffect(() => {
    setVideoLoading(true);
    let video = videoRef?.getElement();
    if (!video) return;

    let videoSrc = "http://localhost:5000/video/tetris/output.m3u8";

    if (Hls.isSupported()) {
      let hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, function () {
        setVideoLoading(false);
        video.play();
      });
      hls.on(Hls.Events.ERROR, function (event, data) {
        setVideoLoading(false);
        console.error("Error", event, data);
      });
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = videoSrc;
    }
  }, [videoRef]);

  function halfBound(
    bounds: [[number, number], [number, number]],
  ): [[number, number], [number, number]] {
    const [[x1, y1], [x2, y2]] = bounds;

    const centerX = (x1 + x2) / 2;
    const centerY = (y1 + y2) / 2;

    const halfWidth = (x2 - x1) / 4;
    const halfHeight = (y2 - y1) / 4;

    const newX1 = centerX - halfWidth;
    const newY1 = centerY - halfHeight;
    const newX2 = centerX + halfWidth;
    const newY2 = centerY + halfHeight;

    return [
      [newX1, newY1],
      [newX2, newY2],
    ];
  }

  return (
    <MapContainer
      center={[22.2723, 77.7069]}
      zoom={5}
      scrollWheelZoom={true}
      className="flex-1"
      ref={setMap}
    >
      <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <SelectArea
        onBoundsChange={(bounds) => {
          setSelectedArea(bounds);
        }}
        keepRectangle={true}
        options={{
          dashArray: "5, 5",
          weight: 2,
          fillColor: "transparent",
          color: "cadetblue",
        }}
      />
      {selectedArea && (
        <>
          <SVGOverlay
            bounds={halfBound(selectedArea)}
            key={selectedArea.toString() + "-loading"}
            opacity={0.9}
          >
            {videoLoading && <Loader />}
          </SVGOverlay>
          <VideoOverlay
            bounds={selectedArea}
            key={selectedArea.toString() + "-video"}
            url=""
            zIndex={1000}
            autoplay={true}
            loop={true}
            muted={true}
            ref={setVideoRef}
          />
        </>
      )}
    </MapContainer>
  );
}
