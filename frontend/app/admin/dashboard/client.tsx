"use client";

import StatCards from "@/components/admin/dashboard/StatCards";
import GrowthMetrics from "@/components/admin/dashboard/GrowthMetrics";
import SystemHealth from "@/components/admin/dashboard/SystemHealth";
import PeakActivity from "@/components/admin/dashboard/PeakActivity";
import TopPerformers from "@/components/admin/dashboard/TopPerformers";
import GeoDistribution from "@/components/admin/dashboard/GeoDistribution";
import {
    GeoDistResponse,
    GrowthMetricsResponse,
    TopPerformerResponse,
    HealthCheckResponse,
    PeakTimesResponse,
    PlatformStatsResponse,
} from "@/api-types";

export default function AdminDashboard({
    platformStats,
    growthMetrics,
    topPerformers,
    peakTimes,
    geoDistribution,
    systemHealth,
}: {
    platformStats: PlatformStatsResponse;
    growthMetrics: GrowthMetricsResponse;
    topPerformers: TopPerformerResponse[];
    peakTimes: PeakTimesResponse;
    geoDistribution: GeoDistResponse;
    systemHealth: HealthCheckResponse;
}) {
    return (
        <div className="space-y-6 p-6">
            <div>
                <h1 className="text-3xl font-bold text-text-main mb-2">
                    Dashboard Overview
                </h1>
            </div>

            <StatCards platformStats={platformStats} />

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 h-full">
                    <GrowthMetrics growthMetrics={growthMetrics} />
                </div>
                <div className="space-y-6">
                    <SystemHealth healthReport={systemHealth} />
                    <PeakActivity peakTimes={peakTimes} />
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-1 gap-6">
                <TopPerformers topPerformers={topPerformers} />
                <GeoDistribution geoDistribution={geoDistribution} />
            </div>
        </div>
    );
}
