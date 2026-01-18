"use client";

import { TopPerformerResponse, TopPerformersResponse } from "@/api-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

export default function TopPerformers({
    topPerformers,
}: {
    topPerformers: TopPerformerResponse[];
}) {
    return (
        <Card className="bg-surface border-none">
            <CardHeader className="flex flex-row items-center justify-between pb-4">
                <div>
                    <CardTitle className="text-text-main">
                        Top Performers
                    </CardTitle>
                </div>
                <p className="text-xs text-text-muted">Last 30 Days</p>
            </CardHeader>
            <CardContent>
                <Table>
                    <TableHeader>
                        <TableRow className="border-border-subtle hover:bg-transparent">
                            <TableHead className="text-text-muted font-medium uppercase text-xs tracking-wider">
                                Rank
                            </TableHead>
                            <TableHead className="text-text-muted font-medium uppercase text-xs tracking-wider">
                                Short URL
                            </TableHead>
                            <TableHead className="text-text-muted font-medium uppercase text-xs tracking-wider text-right">
                                Clicks
                            </TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {topPerformers.map((performer) => (
                            <TableRow
                                key={performer.rank}
                                className="border-border-subtle hover:bg-surface-hover"
                            >
                                <TableCell className="font-medium">
                                    <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-brand-blue/10 text-brand-blue font-bold text-sm">
                                        #{performer.rank + 1}
                                    </span>
                                </TableCell>
                                <TableCell className="text-text-main font-mono">
                                    {performer.details.short_url}
                                </TableCell>
                                <TableCell className="text-text-main font-bold text-right">
                                    {performer.metric_value.toLocaleString()}
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </CardContent>
        </Card>
    );
}
