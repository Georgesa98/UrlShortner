"use server";

import { toast } from "sonner";
import { fetchUrls } from "./server";
import MyUrls from "./client";

export default async function Page({
    searchParams,
}: {
    searchParams: Promise<{
        [key: string]: string | string[] | undefined;
    }>;
}) {
    const params = await searchParams;
    const data = await fetchUrls({
        page: (params.page as string) || "1",
        limit: (params.limit as string) || "4",
    });
    console.log(data);

    return <MyUrls data={data.data} />;
}
