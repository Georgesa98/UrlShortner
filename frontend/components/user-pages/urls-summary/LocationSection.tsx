"use client";

import { Card, CardContent } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Globe } from "lucide-react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import worldCountries from "world-countries";
import { GetUrlSummaryResponse } from "@/api-types";

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png",
    iconUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png",
    shadowUrl:
        "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png",
});

interface LocationSectionProps {
    data: GetUrlSummaryResponse;
}

const getCountryCoordinates = (
    countryName: string
): [number, number] | null => {
    const country = worldCountries.find(
        (c) =>
            c.name.common.toLowerCase() === countryName.toLowerCase() ||
            c.name.official.toLowerCase() === countryName.toLowerCase() ||
            c.cca2.toLowerCase() === countryName.toLowerCase() ||
            c.cca3.toLowerCase() === countryName.toLowerCase()
    );

    if (country && country.latlng) {
        return [country.latlng[0], country.latlng[1]];
    }

    return null;
};

export default function LocationSection({ data }: LocationSectionProps) {
    const locationData = data.top_metrics.countries.map((country) => ({
        country: country.geolocation,
        visitors: country.count,
        percentage: parseFloat(
            (
                (country.count / Math.max(data.basic_info.visits, 1)) *
                100
            ).toFixed(2)
        ),
    }));

    const maxVisitors = Math.max(...locationData.map((loc) => loc.visitors), 1);
    const getRadius = (visitors: number) => {
        return Math.max(
            5,
            Math.min(20, visitors / Math.max(maxVisitors / 20, 1))
        );
    };

    return (
        <Card className="mb-6">
            <CardContent className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-bold">Locations</h2>
                    <Globe className="h-5 w-5 text-muted-foreground" />
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="h-75">
                        <MapContainer
                            center={[20, 0]}
                            zoom={2}
                            style={{
                                height: "100%",
                                width: "100%",
                                borderRadius: "0.5rem",
                            }}
                            scrollWheelZoom={false}
                        >
                            <TileLayer
                                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                            />
                            {locationData.map((location, index) => {
                                const coordinates = getCountryCoordinates(
                                    location.country
                                );

                                if (!coordinates) {
                                    return null;
                                }

                                return (
                                    <CircleMarker
                                        key={`marker-${index}`}
                                        center={coordinates}
                                        radius={getRadius(location.visitors)}
                                        color="#4f46e5"
                                        fillColor="#6366f1"
                                        fillOpacity={0.7}
                                        weight={1}
                                    >
                                        <Popup>
                                            {location.country}:{" "}
                                            {location.visitors} visitors
                                        </Popup>
                                    </CircleMarker>
                                );
                            })}
                        </MapContainer>
                    </div>

                    <div>
                        <h3 className="font-medium mb-4">Country Statistics</h3>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Country</TableHead>
                                    <TableHead>Visitors</TableHead>
                                    <TableHead>Percentage</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {locationData.map((location, index) => (
                                    <TableRow key={index}>
                                        <TableCell className="font-medium">
                                            {location.country}
                                        </TableCell>
                                        <TableCell>
                                            {location.visitors.toLocaleString()}
                                        </TableCell>
                                        <TableCell>
                                            {location.percentage}%
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                        </Table>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
