"use client";

import dynamic from "next/dynamic";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import AnalyticsHeader from "@/components/user-pages/urls-summary/AnalyticsHeader";
import MetricsCards from "@/components/user-pages/urls-summary/MetricsCards";
import TrafficChart from "@/components/user-pages/urls-summary/TrafficChart";
import DeviceBrowserSection from "@/components/user-pages/urls-summary/DeviceBrowserSection";
import TopReferrersTable from "@/components/user-pages/urls-summary/TopReferrersTable";

// Dynamically import LocationSection with SSR disabled (leaflet needs browser window)
const LocationSection = dynamic(
    () => import("@/components/user-pages/urls-summary/LocationSection"),
    { 
        ssr: false,
        loading: () => (
            <div className="mb-6 p-6 bg-card rounded-lg border animate-pulse">
                <div className="h-64 bg-muted rounded"></div>
            </div>
        )
    }
);

interface BasicInfo {
    id: number;
    long_url: string;
    short_url: string;
    created_at: string;
    updated_at: string;
    visits: number;
    unique_visits: number;
    expiry_date: string;
}

interface DailyVisit {
    date: string;
    daily_visits: number;
    unique_visits: number;
}

interface UniqueVsTotal {
    unique: number;
    total: number;
}

interface Analytics {
    daily_visits: DailyVisit[];
    unique_vs_total: UniqueVsTotal;
}

interface DeviceMetric {
    device: string;
    count: number;
}

interface BrowserMetric {
    browser: string;
    count: number;
}

interface OperatingSystemMetric {
    operating_system: string;
    count: number;
}

interface CountryMetric {
    geolocation: string;
    count: number;
}

interface TopMetrics {
    devices: DeviceMetric[];
    browsers: BrowserMetric[];
    operating_systems: OperatingSystemMetric[];
    countries: CountryMetric[];
}

interface RecentVisitor {
    id: number;
    timestamp: string;
    hashed_ip: string;
    referer: string;
    geolocation: string;
    browser: string;
    operating_system: string;
    device: string;
    new_visitor: boolean;
    url: number;
}

interface BackendUrlAnalyticsData {
    basic_info: BasicInfo;
    analytics: Analytics;
    top_metrics: TopMetrics;
    recent_visitors: RecentVisitor[];
}

export default function SpecificUrl({
    data,
}: {
    data: BackendUrlAnalyticsData;
}) {
    const router = useRouter();
    const pathname = usePathname();
    const searchParams = useSearchParams();
    
    // Get current days from URL params, default to 7
    const currentDays = searchParams.get("days") ? parseInt(searchParams.get("days")!, 10) : 7;

    const handleDaysChange = (days: number) => {
        const params = new URLSearchParams(searchParams.toString());
        params.set("days", days.toString());
        router.push(`${pathname}?${params.toString()}`, { scroll: false });
    };

    console.log("Backend data:", data);

    return (
        <div className="container mx-auto py-6 px-4 md:px-8">
            <AnalyticsHeader 
                data={data} 
                currentDays={currentDays}
                onDaysChange={handleDaysChange}
            />

            <MetricsCards data={data} />

            <TrafficChart data={data} />

            <LocationSection data={data} />

            <DeviceBrowserSection data={data} />

            <TopReferrersTable data={data} />
        </div>
    );
}
