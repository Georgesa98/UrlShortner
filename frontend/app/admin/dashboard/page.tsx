"use server";

import AdminDashboard from "./client";
import {
    growthMetricsAction,
    peakTimesAction,
    platformStatsAction,
    topPerformersAction,
    geoDistributionAction,
    systemHealthAction,
} from "./server";
export default async function Page() {
    const now = new Date();
    const sevenDaysAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
    const systemHealth = await systemHealthAction();
    const platformStats = await platformStatsAction({
        time_range: sevenDaysAgo.toISOString(),
    });
    const growthMetrics = await growthMetricsAction();
    const topPerformers = await topPerformersAction({
        metric: "clicks",
        limit: 10,
    });
    const peakTimes = await peakTimesAction();
    const geoDistribution = await geoDistributionAction();
    return (
        <AdminDashboard
            platformStats={platformStats.data}
            growthMetrics={growthMetrics.data}
            topPerformers={topPerformers.data}
            peakTimes={peakTimes.data}
            geoDistribution={geoDistribution.data}
            systemHealth={systemHealth.data}
        />
    );
}
