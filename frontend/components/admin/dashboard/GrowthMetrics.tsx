"use client";

import { GrowthMetricsResponse } from "@/api-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
    ChartLegend,
    ChartLegendContent,
} from "@/components/ui/chart";
import { AreaChart, Area, CartesianGrid, XAxis, YAxis } from "recharts";

const chartConfig = {
    clicks: {
        label: "Clicks Volume",
        color: "#007bff",
    },
    users: {
        label: "User Growth",
        color: "#10b981",
    },
    urls: {
        label: "URL Growth",
        color: "#f59e0b",
    },
};

export default function GrowthMetrics({
    growthMetrics,
}: {
    growthMetrics: GrowthMetricsResponse;
}) {
    const chartData = [
        {
            day: "MON",
            clicks: growthMetrics.metrics?.clicks_volume?.[0]?.clicks,
            users: growthMetrics.metrics?.users_growth?.[0]?.new_users,
            urls: growthMetrics.metrics?.urls_growth?.[0]?.new_urls,
        },
        {
            day: "TUE",
            clicks: growthMetrics.metrics?.clicks_volume?.[1]?.clicks,
            users: growthMetrics.metrics?.users_growth?.[1]?.new_users,
            urls: growthMetrics.metrics?.urls_growth?.[1]?.new_urls,
        },
        {
            day: "WED",
            clicks: growthMetrics.metrics?.clicks_volume?.[2]?.clicks,
            users: growthMetrics.metrics?.users_growth?.[2]?.new_users,
            urls: growthMetrics.metrics?.urls_growth?.[2]?.new_urls,
        },
        {
            day: "THU",
            clicks: growthMetrics.metrics?.clicks_volume?.[3]?.clicks,
            users: growthMetrics.metrics?.users_growth?.[3]?.new_users,
            urls: growthMetrics.metrics?.urls_growth?.[3]?.new_urls,
        },
        {
            day: "FRI",
            clicks: growthMetrics.metrics?.clicks_volume?.[4]?.clicks,
            users: growthMetrics.metrics?.users_growth?.[4]?.new_users,
            urls: growthMetrics.metrics?.urls_growth?.[4]?.new_urls,
        },
        {
            day: "SAT",
            clicks: growthMetrics.metrics?.clicks_volume?.[5]?.clicks,
            users: growthMetrics.metrics?.users_growth?.[5]?.new_users,
            urls: growthMetrics.metrics?.urls_growth?.[5]?.new_urls,
        },
        {
            day: "SUN",
            clicks: growthMetrics.metrics?.clicks_volume?.[6]?.clicks,
            users: growthMetrics.metrics?.users_growth?.[6]?.new_users,
            urls: growthMetrics.metrics?.urls_growth?.[6]?.new_urls,
        },
    ];
    console.log(growthMetrics);
    return (
        <Card className="bg-surface border-none h-full">
            <CardHeader>
                <CardTitle className="text-text-main">Growth Metrics</CardTitle>
                <p className="text-sm text-text-muted">
                    Weekly Volume Overview
                </p>
            </CardHeader>
            <CardContent className="h-full">
                <ChartContainer config={chartConfig} className="h-full w-full">
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient
                                id="fillClicks"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor="#007bff"
                                    stopOpacity={0.3}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="#007bff"
                                    stopOpacity={0}
                                />
                            </linearGradient>
                            <linearGradient
                                id="fillUsers"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor="#10b981"
                                    stopOpacity={0.3}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="#10b981"
                                    stopOpacity={0}
                                />
                            </linearGradient>
                            <linearGradient
                                id="fillUrls"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor="#f59e0b"
                                    stopOpacity={0.3}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="#f59e0b"
                                    stopOpacity={0}
                                />
                            </linearGradient>
                        </defs>
                        <CartesianGrid
                            strokeDasharray="3 3"
                            stroke="#334155"
                            opacity={0.3}
                        />
                        <XAxis
                            dataKey="day"
                            stroke="#94a3b8"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                        />
                        <YAxis
                            stroke="#94a3b8"
                            fontSize={12}
                            tickLine={false}
                            axisLine={false}
                        />
                        <ChartTooltip content={<ChartTooltipContent />} />
                        <ChartLegend content={<ChartLegendContent />} />
                        <Area
                            type="monotone"
                            dataKey="clicks"
                            stroke="#007bff"
                            strokeWidth={2}
                            fill="url(#fillClicks)"
                        />
                        <Area
                            type="monotone"
                            dataKey="users"
                            stroke="#10b981"
                            strokeWidth={2}
                            fill="url(#fillUsers)"
                            strokeDasharray="5 5"
                        />
                        <Area
                            type="monotone"
                            dataKey="urls"
                            stroke="#f59e0b"
                            strokeWidth={2}
                            fill="url(#fillUrls)"
                        />
                    </AreaChart>
                </ChartContainer>
            </CardContent>
        </Card>
    );
}
