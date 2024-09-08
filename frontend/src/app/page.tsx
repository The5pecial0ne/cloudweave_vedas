"use client";

import { CodeViewer } from "@/components/playground/code-viewer";
import { PresetShare } from "@/components/playground/preset-share";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { LocateIcon } from "lucide-react";
import { Label } from "@/components/ui/label";
import { ComboInput } from "@/components/combo-input";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function PlaygroundPage() {
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

        <div className="flex-1 grid grid-cols-[1fr_230px] p-8 py-6 gap-8">
          <div className="flex flex-1 h-full flex-col space-y-4">
            <Textarea
              placeholder="Write a tagline for an ice cream shop"
              className="min-h-[400px] flex-1 p-4 md:min-h-[700px] lg:min-h-[700px] resize-none"
            />
          </div>

          <Tabs defaultValue="complete">
            <div className="h-full">
              <div className="grid h-full items-stretch gap-6">
                <div className="flex-col gap-y-2 sm:flex md:order-2">
                  <div>
                    <Label htmlFor="baseMap">Base Map</Label>
                    <div className="h-1" />

                    <ComboInput
                      data={[
                        { label: "Mapbox", value: "mapbox" },
                        { label: "Google Maps", value: "google-maps" },
                        { label: "OpenStreetMap", value: "openstreetmap" },
                      ]}
                      type="base map"
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
                      placeholder="43.12"
                    />

                    <Label htmlFor="longitude">Longitude</Label>
                    <Input
                      type="text"
                      id="longitude"
                      className="input"
                      placeholder="83.21"
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
