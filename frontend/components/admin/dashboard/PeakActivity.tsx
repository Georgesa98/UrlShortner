"use client";

import { PeakTimesResponse } from "@/api-types";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function PeakActivity({
    peakTimes,
}: {
    peakTimes: PeakTimesResponse;
}) {
    return (
        <Card className="bg-surface border-none">
            <CardHeader>
                <CardTitle className="text-text-main">Peak Activity</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="grid grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <p className="text-xs font-bold uppercase tracking-widest text-text-muted">
                            Peak Day
                        </p>
                        <p className="text-3xl font-bold text-brand-blue">
                            {peakTimes.day.peak_day}
                        </p>
                        <p className="text-md text-text-muted">
                            {peakTimes.day.avg_clicks} average clicks
                        </p>
                    </div>
                    <div className="space-y-2">
                        <p className="text-xs font-bold uppercase tracking-widest text-text-muted">
                            Peak Hour
                        </p>
                        <p className="text-3xl font-bold text-brand-blue">
                            {peakTimes.hour.peak_hour}
                        </p>
                        <p className="text-md text-text-muted">
                            {peakTimes.hour.avg_clicks} average clicks
                        </p>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
