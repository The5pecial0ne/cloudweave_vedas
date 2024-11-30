import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LocateIcon } from "lucide-react";
import { Label } from "@/components/ui/label";
import { ComboInput } from "@/components/combo-input";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useEffect, useState } from "react";
import { MapContainer, TileLayer, VideoOverlay } from "react-leaflet";
import SelectArea from "@/components/select-area";
import { Map, VideoOverlay as LeafletVideoOverlay } from "leaflet";
import Hls from "hls.js";

export default function PlaygroundPage() {
  const [map, setMap] = useState<Map | null>(null);
  const [videoRef, setVideoRef] = useState<LeafletVideoOverlay | null>(null);

  const [lng, setLng] = useState<string | number>(77.7069);
  const [lat, setLat] = useState<string | number>(22.2723);
  const [zoom, setZoom] = useState(4.07);

  const [selectedArea, setSelectedArea] = useState<
    [[number, number], [number, number]] | null
  >(null);

  useEffect(() => {
    if (map) {
      map.on("move", () => {
        setLat(map.getCenter().lat.toFixed(4));
        setLng(map.getCenter().lng.toFixed(4));
        setZoom(map.getZoom());
      });
    }
  }, [map]);

  useEffect(() => {
    let video = videoRef?.getElement();
    if (!video) return;

    let videoSrc = "http://localhost:5000/video/tetris/output.m3u8";

    if (Hls.isSupported()) {
      let hls = new Hls();
      hls.loadSource(videoSrc);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, function () {
        video.play();
      });
      hls.on(Hls.Events.ERROR, function (event, data) {
        console.error("Error", event, data);
      })
    } else if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = videoSrc;
    }
  }, [videoRef]);

  return (
    <div className="h-screen">
      <div className="hidden h-full flex-col md:flex">
        <div className="px-8 flex flex-col items-start justify-between space-y-2 py-4 sm:flex-row sm:items-center sm:space-y-0 md:h-16">
          <h2 className="text-lg font-semibold">Cloudweave</h2>
          <div className="ml-auto flex w-full space-x-2 sm:justify-end">
            <div className="hidden space-x-2 md:flex">
              <Button variant="secondary">Save</Button>
              <Button variant="secondary">View code</Button>
              <Button variant="secondary">Share</Button>
            </div>
          </div>
        </div>

        <Separator />

        <div className="flex-1 flex p-8 py-6 gap-8">
          <div className="w-full flex-1 overflow-hidden rounded-lg bg-white relative flex">
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
                  fillColor: "transparent",
                  color: "cadetblue",
                }}
              />
              {selectedArea && (
                <VideoOverlay
                  bounds={selectedArea}
                  key={selectedArea.toString()}
                  url="https://www.mapbox.com/bites/00188/patricia_nasa.webm"
                  zIndex={1000}
                  autoplay={true}
                  loop={true}
                  muted={true}
                  ref={setVideoRef}
                />
              )}
            </MapContainer>
          </div>

          <Tabs defaultValue="complete" className="flex-shrink-0">
            <div className="h-full">
              <div className="grid h-full items-stretch gap-6">
                <div className="flex-col gap-y-2 sm:flex md:order-2">
                  <div>
                    <Label htmlFor="baseMap">Base Map</Label>
                    <div className="h-1" />

                    <ComboInput
                      data={[
                        {
                          label: "Street",
                          value: "mapbox://styles/mapbox/streets-v12",
                        },
                        {
                          label: "Satellite",
                          value: "mapbox://styles/mapbox/satellite-v9",
                        },
                        {
                          label: "Satellite Streets",
                          value: "mapbox://styles/mapbox/satellite-streets-v11",
                        },
                        {
                          label: "Dark",
                          value: "mapbox://styles/mapbox/dark-v10",
                        },
                        {
                          label: "Light",
                          value: "mapbox://styles/mapbox/light-v10",
                        },
                        {
                          label: "Outdoors",
                          value: "mapbox://styles/mapbox/outdoors-v11",
                        },
                        {
                          label: "Navigation",
                          value:
                            "mapbox://styles/mapbox/navigation-guidance-day-v4",
                        },
                      ]}
                      type="base map"
                    />
                  </div>

                  <div>
                    <Label htmlFor="satellite">Satellite</Label>
                    <div className="h-1" />

                    <ComboInput
                      data={[{ label: "INSAT-3D", value: "INSAT-3D" }]}
                      defaultValue={"INSAT-3D"}
                      type="satellite"
                    />
                  </div>

                  <div>
                    <Label htmlFor="overlay">Overlay</Label>
                    <div className="h-1" />

                    <ComboInput
                      data={[
                        { label: "None", value: "" },
                        {
                          label: "Cyclone Maharashtra",
                          value: "/IMG_8376.MP4",
                        },
                        { label: "Hourly Timelapse", value: "/IMG_8377.MP4" },
                      ]}
                      type="overlay"
                    />
                  </div>

                  <div className="grid gap-2 mt-4">
                    <span className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70">
                      Mode
                    </span>
                    <TabsList className="grid grid-cols-1">
                      <TabsTrigger value="complete">
                        <span className="sr-only">Complete</span>
                        <LocateIcon className="h-5 w-5" />
                      </TabsTrigger>
                    </TabsList>
                  </div>

                  <div className="grid grid-cols-[1fr_2fr] items-center gap-y-3">
                    <Label htmlFor="latitude">Latitude</Label>
                    <Input
                      type="text"
                      id="latitude"
                      className="input"
                      value={lat}
                      readOnly
                    />

                    <Label htmlFor="longitude">Longitude</Label>
                    <Input
                      type="text"
                      id="longitude"
                      className="input"
                      value={lng}
                      readOnly
                    />

                    <Label htmlFor="zoom">Zoom</Label>
                    <Input
                      type="text"
                      id="zoom"
                      className="input"
                      value={zoom}
                      readOnly
                    />
                  </div>
                </div>
              </div>
            </div>
          </Tabs>
        </div>
      </div>
    </div>
  );
}
