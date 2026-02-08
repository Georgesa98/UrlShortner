"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ChevronLeft, ExternalLink, Eye, Globe } from "lucide-react";
import Link from "next/link";
import { GetUrlSummaryResponse } from "@/api-types";

interface AnalyticsHeaderProps {
  data: GetUrlSummaryResponse;
  currentDays: number;
  onDaysChange: (days: number) => void;
}

export default function AnalyticsHeader({ data, currentDays, onDaysChange }: AnalyticsHeaderProps) {
  const urlTitle = data.basic_info.long_url;
  const urlStatus = data.basic_info.url_status.state;
  const urlLink = data.basic_info.short_url;
  return (
    <Card className="mb-6">
      <CardContent className="py-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <Link href="/urls">
              <Button variant="outline" size="icon">
                <ChevronLeft className="h-4 w-4" />
              </Button>
            </Link>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold">{urlTitle}</h1>
                <span
                  className={`rounded-lg px-1.5 py-0.5 text-[10px] font-bold ${
                    urlStatus === "ACTIVE"
                      ? "bg-green-500/10 text-green-500"
                      : urlStatus === "EXPIRED"
                      ? "bg-yellow-500/10 text-yellow-500"
                      : urlStatus === "FLAGGED"
                      ? "bg-orange-500/10 text-orange-500"
                      : "bg-red-500/10 text-red-500"
                  }`}
                >
                  {urlStatus}
                </span>
              </div>
              <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                <Globe className="h-3 w-3" />
                <span>{urlLink}</span>
                <Link href={urlLink} target="_blank">
                  <ExternalLink className="h-3 w-3 ml-1" />
                </Link>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 text-sm">
              <Eye className="h-4 w-4 text-muted-foreground" />
              <span className="font-medium">{data.basic_info.visits}</span>
              <span className="text-muted-foreground">views</span>
            </div>

            <Select 
              value={currentDays.toString()}
              onValueChange={(value) => onDaysChange(parseInt(value, 10))}
            >
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Select date range" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="1">Today</SelectItem>
                <SelectItem value="7">Last 7 days</SelectItem>
                <SelectItem value="30">Last 30 days</SelectItem>
                <SelectItem value="90">Last 90 days</SelectItem>
                <SelectItem value="365">This year</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
