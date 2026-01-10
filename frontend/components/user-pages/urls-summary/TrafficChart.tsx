"use client";

import { Area, Line, AreaChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { Card, CardContent } from "@/components/ui/card";
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
} from "@/components/ui/chart";
import { GetUrlSummaryResponse } from "@/api-types";

interface TrafficChartProps {
    data: GetUrlSummaryResponse;
}

export default function TrafficChart({ data }: TrafficChartProps) {
    const trafficData = data.analytics.daily_visits.map((daily) => ({
        date: daily.date,
        visitors: daily.daily_visits,
    }));
    return (
        <Card className="mb-6">
            <CardContent className="p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-bold">Traffic Overview</h2>
                </div>

                <ChartContainer
                    config={{
                        visitors: {
                            label: "Visitors",
                            color: "#3b82f6",
                        },
                    }}
                    className="h-75 w-full"
                >
                    <AreaChart accessibilityLayer data={trafficData}>
                        <CartesianGrid vertical={false} />
                        <XAxis
                            dataKey="date"
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                        />
                        <YAxis
                            tickLine={false}
                            axisLine={false}
                            tickMargin={8}
                        />
                        <ChartTooltip
                            cursor={false}
                            content={<ChartTooltipContent />}
                        />
                        <defs>
                            <linearGradient
                                id="colorVisitors"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor="#3b82f6"
                                    stopOpacity={0.8}
                                />
                                <stop
                                    offset="95%"
                                    stopColor="#3b82f6"
                                    stopOpacity={0.1}
                                />
                            </linearGradient>
                        </defs>
                        <Area
                            dataKey="visitors"
                            type="monotone"
                            fill="url(#colorVisitors)"
                            stroke="none"
                        />
                        <Line
                            dataKey="visitors"
                            type="monotone"
                            stroke="#3b82f6"
                            strokeWidth={2}
                            dot={{ r: 4 }}
                            activeDot={{ r: 6 }}
                        />
                    </AreaChart>
                </ChartContainer>
            </CardContent>
        </Card>
    );
}
