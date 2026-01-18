"use client";

import { GeoDistResponse } from "@/api-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { Globe } from "lucide-react";

interface GeoData {
    country: string;
    volume: string;
    percentage: number;
    color: string;
}

export default function GeoDistribution({
    geoDistribution,
}: {
    geoDistribution: GeoDistResponse;
}) {
    const geoData: GeoData[] = [
        {
            country: "United States",
            volume: "18.4M",
            percentage: 41,
            color: "#007bff",
        },
        {
            country: "United Kingdom",
            volume: "7.2M",
            percentage: 16,
            color: "#007bff",
        },
        {
            country: "Germany",
            volume: "5.4M",
            percentage: 12,
            color: "#007bff",
        },
    ];

    return (
        <Card className="bg-surface border-none">
            <CardHeader className="flex flex-row items-center justify-between pb-4">
                <div>
                    <CardTitle className="text-text-main">
                        Geo Distribution
                    </CardTitle>
                </div>
                <Globe className="h-5 w-5 text-text-muted" />
            </CardHeader>
            <CardContent className="space-y-6">
                {geoData.map((data, index) => (
                    <div key={index} className="space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-text-main">
                                {data.country}
                            </span>
                            <span className="text-sm font-bold text-text-main">
                                {data.volume}{" "}
                                <span className="text-text-muted font-normal">
                                    ({data.percentage}%)
                                </span>
                            </span>
                        </div>
                        <Progress
                            value={data.percentage}
                            className="bg-surface-hover [&>div]:bg-brand-blue"
                        />
                    </div>
                ))}
            </CardContent>
        </Card>
    );
}
