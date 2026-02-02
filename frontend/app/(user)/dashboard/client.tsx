"use client";

import AnalyticCards from "@/components/user-pages/dashboard/AnalyticCards";
import { UrlDataTable } from "../../../components/tables/url/data-table";
import { columns } from "@/components/tables/url/columns";
import { GetTopVisitedUrlsResponse, GetUserStatsResponse } from "@/api-types";

export default function UserDashboard({
  userStats,
  topVisitedUrls,
}: {
  userStats: GetUserStatsResponse;
  topVisitedUrls: GetTopVisitedUrlsResponse;
}) {
  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="font-black text-2xl">Dashboard</h1>
        <p className="text-muted-foreground text-sm">
          Welcome back! Here&apos;s your link performance
        </p>
      </div>
      <AnalyticCards userStats={userStats} />
      <UrlDataTable
        control={false}
        columns={columns}
        data={topVisitedUrls.top_urls}
        pagination={{
          total: 3,
          page: 1,
          limit: 3,
          total_pages: 1,
          has_next: false,
          has_previous: false,
        }}
      />
    </div>
  );
}
