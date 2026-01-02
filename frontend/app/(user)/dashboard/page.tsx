"use client";

import AnalyticCards from "@/components/user-pages/dashboard/AnalyticCards";
import { UrlDataTable } from "../../../components/tables/url/data-table";
import { urlDummyData } from "@/components/tables/url/dummy-data";
import { columns } from "@/components/tables/url/columns";

export default function UserDashboard() {
    return (
        <div className="flex flex-col gap-8">
            <div>
                <h1 className="font-black text-2xl">Dashboard</h1>
                <p className="text-muted-foreground text-sm">
                    Welcome back! Here&apos;s your link performance
                </p>
            </div>
            <AnalyticCards />
            <UrlDataTable columns={columns} data={urlDummyData} />
        </div>
    );
}
