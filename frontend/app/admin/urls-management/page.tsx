"use server";

import UrlsManagementPage from "./client";
import { listUrlsAction, platformStatsAction } from "./server";

export default async function Page() {
    const urlsResponse = await listUrlsAction({ page: 1, limit: 10 });
    const statsResponse = await platformStatsAction();
    return (
        <UrlsManagementPage
            urls={urlsResponse.data.data.urls}
            stats={statsResponse.data}
            pagination={urlsResponse.data.data.pagination}
        />
    );
}
