"use client";

import { useState } from "react";
import { GrowthMetricsResponse } from "@/api-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    ChartContainer,
    ChartTooltip,
    ChartTooltipContent,
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

type MetricTab = 'clicks' | 'users' | 'urls';

export default function GrowthMetrics({
    growthMetrics,
}: {
    growthMetrics: GrowthMetricsResponse;
}) {
    const [activeTab, setActiveTab] = useState<MetricTab>('clicks');
    // Dynamically map all data points from the API response
    const chartData = growthMetrics.metrics?.users_growth?.map((userItem, index) => {
        const clickData = growthMetrics.metrics?.clicks_volume?.[index];
        const urlData = growthMetrics.metrics?.urls_growth?.[index];
        
        // Format the date for display (e.g., "Jan 15")
        const date = new Date(userItem.week_starting);
        const label = date.toLocaleDateString('en-US', { 
            month: 'short', 
            day: 'numeric' 
        });
        
        return {
            week: label,
            clicks: clickData?.clicks || 0,
            users: userItem.new_users || 0,
            urls: urlData?.new_urls || 0,
        };
    }) || [];
    
    console.log(growthMetrics);
    
    const getSubtitle = () => {
        switch (activeTab) {
            case 'clicks':
                return 'Total clicks over time';
            case 'users':
                return 'New users per week';
            case 'urls':
                return 'New URLs created per week';
        }
    };
    
    const getChartColor = () => {
        switch (activeTab) {
            case 'clicks':
                return '#007bff';
            case 'users':
                return '#10b981';
            case 'urls':
                return '#f59e0b';
        }
    };
    
    return (
        <Card className="bg-surface border-none h-full">
            <CardHeader>
                <CardTitle className="text-text-main">Growth Metrics</CardTitle>
                <p className="text-sm text-text-muted mb-4">
                    {getSubtitle()}
                </p>
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('clicks')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            activeTab === 'clicks'
                                ? 'bg-blue-500 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        Clicks
                    </button>
                    <button
                        onClick={() => setActiveTab('users')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            activeTab === 'users'
                                ? 'bg-green-500 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        Users
                    </button>
                    <button
                        onClick={() => setActiveTab('urls')}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            activeTab === 'urls'
                                ? 'bg-orange-500 text-white'
                                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                        }`}
                    >
                        URLs
                    </button>
                </div>
            </CardHeader>
            <CardContent className="h-full">
                <ChartContainer config={chartConfig} className="h-full w-full">
                    <AreaChart data={chartData}>
                        <defs>
                            <linearGradient
                                id="fillMetric"
                                x1="0"
                                y1="0"
                                x2="0"
                                y2="1"
                            >
                                <stop
                                    offset="5%"
                                    stopColor={getChartColor()}
                                    stopOpacity={0.3}
                                />
                                <stop
                                    offset="95%"
                                    stopColor={getChartColor()}
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
                            dataKey="week"
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
                        {activeTab === 'clicks' && (
                            <Area
                                type="monotone"
                                dataKey="clicks"
                                stroke="#007bff"
                                strokeWidth={2}
                                fill="url(#fillMetric)"
                            />
                        )}
                        {activeTab === 'users' && (
                            <Area
                                type="monotone"
                                dataKey="users"
                                stroke="#10b981"
                                strokeWidth={2}
                                fill="url(#fillMetric)"
                            />
                        )}
                        {activeTab === 'urls' && (
                            <Area
                                type="monotone"
                                dataKey="urls"
                                stroke="#f59e0b"
                                strokeWidth={2}
                                fill="url(#fillMetric)"
                            />
                        )}
                    </AreaChart>
                </ChartContainer>
            </CardContent>
        </Card>
    );
}
