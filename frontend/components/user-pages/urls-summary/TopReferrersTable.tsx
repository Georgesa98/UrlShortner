"use client";

import { Card, CardContent } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { TrendingDown, TrendingUp } from "lucide-react";
import { GetUrlSummaryResponse } from "@/api-types";

interface TopReferrersTableProps {
    data: GetUrlSummaryResponse;
}

export default function TopReferrersTable({ data }: TopReferrersTableProps) {
    const referrerMap = new Map();
    data.recent_visitors.forEach((visitor) => {
        const source = visitor.referer || "Direct";
        if (referrerMap.has(source)) {
            referrerMap.set(source, referrerMap.get(source) + 1);
        } else {
            referrerMap.set(source, 1);
        }
    });

    const sortedReferrers = Array.from(referrerMap.entries())
        .map(([source, visitors]) => ({
            source,
            visitors,
            percentage: parseFloat(
                (
                    (visitors / Math.max(data.basic_info.visits, 1)) *
                    100
                ).toFixed(2)
            ),
            trend: "neutral",
        }))
        .sort((a, b) => b.visitors - a.visitors)
        .slice(0, 5);

    const referrerData = sortedReferrers;
    return (
        <Card>
            <CardContent className="p-6">
                <h2 className="text-lg font-bold mb-6">Top Referrers</h2>

                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Source</TableHead>
                            <TableHead>Visitors</TableHead>
                            <TableHead>Percentage</TableHead>
                            <TableHead>Trend</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {referrerData.map((referrer, index) => (
                            <TableRow key={index}>
                                <TableCell className="font-medium">
                                    {referrer.source}
                                </TableCell>
                                <TableCell>
                                    {referrer.visitors.toLocaleString()}
                                </TableCell>
                                <TableCell>{referrer.percentage}%</TableCell>
                                <TableCell>
                                    {referrer.trend === "up" ? (
                                        <span className="flex items-center text-green-500">
                                            <TrendingUp className="h-4 w-4 mr-1" />{" "}
                                            Up
                                        </span>
                                    ) : referrer.trend === "down" ? (
                                        <span className="flex items-center text-red-500">
                                            <TrendingDown className="h-4 w-4 mr-1" />{" "}
                                            Down
                                        </span>
                                    ) : (
                                        <span className="flex items-center text-gray-500">
                                            —
                                        </span>
                                    )}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
