"use client";

import { Card, CardContent } from "@/components/ui/card";
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
    ChartLegend,
    ChartLegendContent,
} from "@/components/ui/chart";
import { Pie, PieChart } from "recharts";
import { Monitor, Smartphone } from "lucide-react";
import { GetUrlSummaryResponse } from "@/api-types";

interface DeviceBrowserSectionProps {
    data: GetUrlSummaryResponse;
}

export default function DeviceBrowserSection({
    data,
}: DeviceBrowserSectionProps) {
    const COLORS = ["#3b82f6", "#ef4444", "#10b981", "#f59e0b", "#8b5cf6"];

    const deviceData = data.top_metrics.devices.map((device, index) => ({
        name: device.device,
        value: device.count,
        fill: COLORS[index % COLORS.length],
    }));

    const browserData = data.top_metrics.browsers.map((browser, index) => ({
        name: browser.browser,
        value: browser.count,
        fill: COLORS[index % COLORS.length],
    }));

    return (
        <Card className="mb-6">
            <CardContent className="p-6">
                <h2 className="text-lg font-bold mb-6">Device & Browser</h2>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Device Distribution */}
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <Monitor className="h-4 w-4 text-muted-foreground" />
                            <h3 className="font-medium">Device Distribution</h3>
                        </div>
                        <ChartContainer
                            config={deviceData.reduce((config, item) => {
                                config[item.name] = {
                                    label: item.name,
                                    color: item.fill,
                                };
                                return config;
                            }, {} as Record<string, { label: string; color: string }>)}
                            className="mx-auto aspect-square max-h-62.5"
                        >
                            <PieChart>
                                <ChartTooltip
                                    content={
                                        <ChartTooltipContent
                                            hideLabel
                                            nameKey="name"
                                        />
                                    }
                                />
                                <Pie
                                    data={deviceData}
                                    dataKey="value"
                                    nameKey="name"
                                    innerRadius={60}
                                    strokeWidth={5}
                                />
                                <ChartLegend
                                    content={<ChartLegendContent />}
                                    className="-translate-y-2 flex-wrap gap-4 *:basis-1/4 *:justify-center"
                                />
                            </PieChart>
                        </ChartContainer>
                    </div>

                    {/* Browser Distribution */}
                    <div>
                        <div className="flex items-center gap-2 mb-4">
                            <Smartphone className="h-4 w-4 text-muted-foreground" />
                            <h3 className="font-medium">
                                Browser Distribution
                            </h3>
                        </div>
                        <ChartContainer
                            config={browserData.reduce((config, item) => {
                                config[item.name] = {
                                    label: item.name,
                                    color: item.fill,
                                };
                                return config;
                            }, {} as Record<string, { label: string; color: string }>)}
                            className="mx-auto aspect-square max-h-62.5"
                        >
                            <PieChart>
                                <ChartTooltip
                                    content={
                                        <ChartTooltipContent
                                            hideLabel
                                            nameKey="name"
                                        />
                                    }
                                />
                                <Pie
                                    data={browserData}
                                    dataKey="value"
                                    nameKey="name"
                                    innerRadius={60}
                                    strokeWidth={5}
                                />
                                <ChartLegend
                                    content={<ChartLegendContent />}
                                    className="-translate-y-2 flex-wrap gap-4 *:basis-1/4 *:justify-center"
                                />
                            </PieChart>
                        </ChartContainer>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
