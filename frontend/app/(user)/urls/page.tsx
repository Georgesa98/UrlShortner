"use server";

import { fetchUrlsAction } from "./server";
import MyUrls from "./client";

export default async function Page({
    searchParams,
}: {
    searchParams: Promise<{
        [key: string]: string | string[] | undefined;
    }>;
}) {
    const params = await searchParams;

    const page = (params.page as string) || "1";
    const limit = (params.limit as string) || "4";
    const status = (params.status as string) || "ALL";
    const date_order = (params.date_order as string) || "DESC";
    const query = (params.query as string) || "";
    const data = await fetchUrlsAction({
        limit: limit,
        page: page,
        status: status,
        date_order: date_order,
        query: query,
    });
    return <MyUrls data={data.data} />;
}
