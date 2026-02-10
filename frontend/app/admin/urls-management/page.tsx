"use server";

import UrlsManagementPage from "./client";
import { listUrlsAction, platformStatsAction } from "./server";

export default async function Page({
    searchParams,
}: {
    searchParams: Promise<{
        [key: string]: string | string[] | undefined;
    }>;
}) {
    const params = await searchParams;
    const page = (params.page as string) || "1";
    const limit = (params.limit as string) || "10";
    const query = (params.query as string) || "";
    const url_status = params.url_status as string | undefined;
    const date_order = params.date_order as string | undefined;
    const urlsResponse = await listUrlsAction({
        page: parseInt(page),
        limit: parseInt(limit),
        query: query,
        url_status,
        date_order,
    });
    const statsResponse = await platformStatsAction();
    return (
        <UrlsManagementPage
            urls={urlsResponse.data.data.urls}
            stats={statsResponse.data}
            pagination={urlsResponse.data.data.pagination}
        />
    );
}
