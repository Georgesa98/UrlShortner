"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
    MousePointerClick,
    Link as LinkIcon,
    UserPlus,
    Eye,
} from "lucide-react";
import { PlatformStatsResponse } from "@/api-types";

interface StatCardProps {
    title: string;
    value: string;
    icon: React.ReactNode;
}

const StatCard = ({ title, value, icon }: StatCardProps) => {
    return (
        <Card className="bg-surface border-none">
            <CardContent className="p-6">
                <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                            <div className="text-brand-blue">{icon}</div>
                            <p className="text-xs font-medium text-text-muted uppercase tracking-wider">
                                {title}
                            </p>
                        </div>
                        <div className="flex items-baseline gap-3">
                            <h3 className="text-3xl font-bold text-text-main">
                                {value}
                            </h3>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default function StatCards({
    platformStats,
}: {
    platformStats: PlatformStatsResponse;
}) {
    const stats = [
        {
            title: "Total Clicks",
            value: platformStats.total_clicks.toLocaleString(),
            icon: <MousePointerClick className="h-5 w-5" />,
        },
        {
            title: "New URLs",
            value: platformStats.new_urls.toLocaleString(),
            icon: <LinkIcon className="h-5 w-5" />,
        },
        {
            title: "New Users",
            value: platformStats.new_users.toLocaleString(),
            icon: <UserPlus className="h-5 w-5" />,
        },
        {
            title: "New Visitors",
            value: platformStats.new_visitors.toLocaleString(),
            icon: <Eye className="h-5 w-5" />,
        },
    ];

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {stats.map((stat, index) => (
                <StatCard key={index} {...stat} />
            ))}
        </div>
    );
}
