"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Database, Network, Zap } from "lucide-react";
import { HealthCheckResponse } from "@/api-types";

interface ServiceStatus {
    name: string;
    status: "healthy" | "degraded" | "unhealthy";
    latency: number;
    icon: React.ReactNode;
}

interface ResourceUsage {
    name: string;
    percentage: number;
}

export default function SystemHealth({
    healthReport,
}: {
    healthReport: HealthCheckResponse;
}) {
    const services: ServiceStatus[] = [
        {
            name: "PostgreSQL",
            status: healthReport.components.database.status,
            latency: healthReport.components.database.latency_ms,
            icon: <Database className="h-4 w-4" />,
        },
        {
            name: "Redis Cache",
            status: healthReport.components.redis.status,
            latency: healthReport.components.redis.latency_ms,
            icon: <Network className="h-4 w-4" />,
        },
        {
            name: "Celery Workers",
            status: healthReport.components.celery.status,
            latency: healthReport.components.celery.latency_ms,
            icon: <Zap className="h-4 w-4" />,
        },
    ];

    const resources: ResourceUsage[] = [
        {
            name: "Disk Usage",
            percentage: healthReport.components.disk.percent_used,
        },
        {
            name: "Memory Usage",
            percentage: healthReport.components.memory.percent_used,
        },
    ];

    const getStatusBadge = (status: string, latency: number) => {
        const statusText = status.charAt(0).toUpperCase() + status.slice(1);
        return (
            <>
                <Badge
                    variant={
                        status === "healthy"
                            ? "success"
                            : status === "degraded"
                            ? "secondary"
                            : "destructive"
                    }
                    className="text-sm font-medium "
                >
                    {latency} ms
                </Badge>
                <Badge
                    variant={
                        status === "healthy"
                            ? "success"
                            : status === "degraded"
                            ? "secondary"
                            : "destructive"
                    }
                    className="text-xs font-bold"
                >
                    {statusText}
                </Badge>
            </>
        );
    };

    return (
        <Card className="bg-surface border-none">
            <CardHeader>
                <CardTitle className="text-text-main">System Health</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
                <div className="space-y-4">
                    {services.map((service, index) => (
                        <div
                            key={index}
                            className="flex items-center justify-between"
                        >
                            <div className="flex items-center gap-3">
                                <div className="text-text-muted">
                                    {service.icon}
                                </div>
                                <span className="text-sm font-medium text-text-main">
                                    {service.name}
                                </span>
                            </div>
                            <div className="flex items-center gap-2">
                                {getStatusBadge(
                                    service.status,
                                    service.latency
                                )}
                            </div>
                        </div>
                    ))}
                </div>

                <div className="space-y-4 pt-4 border-t border-border-subtle">
                    {resources.map((resource, index) => (
                        <div key={index} className="space-y-2">
                            <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-text-muted">
                                    {resource.name}
                                </span>
                                <span className="text-sm font-bold text-text-main">
                                    {resource.percentage}%
                                </span>
                            </div>
                            <Progress
                                value={resource.percentage}
                                className={
                                    resource.name === "Disk Usage"
                                        ? "bg-surface-hover [&>div]:bg-brand-blue"
                                        : "bg-surface-hover [&>div]:bg-yellow-500"
                                }
                            />
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
