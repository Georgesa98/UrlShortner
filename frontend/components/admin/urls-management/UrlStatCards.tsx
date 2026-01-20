"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Link, CheckCircle, Clock, MousePointerClick } from "lucide-react";

interface StatCardProps {
    title: string;
    value: string | number;
    icon: React.ReactNode;
    description?: string;
}

const StatCard = ({ title, value, icon, description }: StatCardProps) => {
    return (
        <Card className="bg-surface border-none">
            <CardContent className="p-6">
                <div className="flex items-start justify-between">
                    <div>
                        <p className="text-xs font-medium text-text-muted uppercase tracking-wider mb-1">
                            {title}
                        </p>
                        <h3 className="text-3xl font-bold text-text-main mb-1">
                            {value}
                        </h3>
                        {description && (
                            <p className="text-xs text-text-muted">
                                {description}
                            </p>
                        )}
                    </div>
                    <div className="p-3 bg-brand-blue/10 rounded-xl text-brand-blue">
                        {icon}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default function UrlStatCards({
    totalUrls = 0,
    activeUrls = 0,
    flaggedUrls = 0,
    inactiveUrls = 0,
}: {
    totalUrls?: number;
    activeUrls?: number;
    flaggedUrls?: number;
    inactiveUrls?: number;
}) {
    const stats = [
        {
            title: "Total URLs",
            value: totalUrls.toLocaleString(),
            icon: <Link className="h-5 w-5" />,
        },
        {
            title: "Active URLs",
            value: activeUrls.toLocaleString(),
            icon: <CheckCircle className="h-5 w-5" />,
        },
        {
            title: "Flagged URLs",
            value: flaggedUrls.toLocaleString(),
            icon: <Clock className="h-5 w-5" />,
        },
        {
            title: "Inactive URLs",
            value: inactiveUrls.toLocaleString(),
            icon: <MousePointerClick className="h-5 w-5" />,
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
