"use client";

import mapboxgl from "mapbox-gl";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { LocateIcon } from "lucide-react";
import { Label } from "@/components/ui/label";
import { ComboInput } from "@/components/combo-input";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useEffect, useRef, useState } from "react";

mapboxgl.accessToken = process.env.NEXT_PUBLIC_MAPBOX_ACCESS_TOKEN!;

export default function PlaygroundPage() {
  const mapContainer = useRef<any>(null);
  const map = useRef<any>(null);
  const [lng, setLng] = useState(77.7069);
  const [lat, setLat] = useState(22.2723);
  const [zoom, setZoom] = useState(4.07);
  const [baseMap, setBaseMap] = useState("mapbox://styles/mapbox/streets-v12");

  useEffect(() => {
    if (map.current) return; // initialize map only once
    map.current = new mapboxgl.Map({
      container: mapContainer.current,
      style: baseMap,
      center: [lng, lat],
      zoom: zoom,
      testMode: true,
    });

    map.current.on('load', function () {
        map.current.resize();
    });

    map.current.on('move', () => {
      setLng(map.current.getCenter().lng.toFixed(4));
      setLat(map.current.getCenter().lat.toFixed(4));
      setZoom(map.current.getZoom().toFixed(2));
    });
  }, []);

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
          <div
            className="h-[800px] w-full flex-1 overflow-hidden rounded-lg shadow-md bg-white"
          >
            <div
              className="h-full w-full"
              ref={mapContainer}
            />
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
                        { label: "Street", value: "mapbox://styles/mapbox/streets-v12" },
                        { label: "Satellite", value: "mapbox://styles/mapbox/satellite-v9" },
                        { label: "Satellite Streets", value: "mapbox://styles/mapbox/satellite-streets-v11" },
                        { label: "Dark", value: "mapbox://styles/mapbox/dark-v10" },
                        { label: "Light", value: "mapbox://styles/mapbox/light-v10" },
                        { label: "Outdoors", value: "mapbox://styles/mapbox/outdoors-v11" },
                        { label: "Navigation", value: "mapbox://styles/mapbox/navigation-guidance-day-v4" },
                      ]}
                      type="base map"
                      defaultValue={baseMap}
                      onValueChange={(value) => {
                        setBaseMap(value);
                        map.current.setStyle(value);
                      }}
                    />
                  </div>

                  <div>
                    <Label htmlFor="satellite">Satellite</Label>
                    <div className="h-1" />

                    <ComboInput
                      data={[
                        { label: "Satellite 1", value: "satellite-1" },
                        { label: "Satellite 2", value: "satellite-2" },
                      ]}
                      type="satellite"
                    />
                  </div>

                  <div>
                    <Label htmlFor="overlay">Overlay</Label>
                    <div className="h-1" />

                    <ComboInput
                      data={[
                        { label: "None", value: "none" },
                        { label: "Cloud Coverage", value: "cloud" },
                      ]}
                      onValueChange={(value) => console.log(value)}
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
