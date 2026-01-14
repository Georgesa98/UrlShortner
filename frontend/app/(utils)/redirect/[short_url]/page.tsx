"use server";

import RedirectPage from "./client";
import NotFound from "./not-found";
import { fetchUrlAction, fetchUrlMetaDataAction } from "./server";
export default async function Page({
    params,
}: {
    params: Promise<{ short_url: string }>;
}) {
    const { short_url } = await params;
    const { data, success, status, message } = await fetchUrlAction(short_url);
    if (success && data?.long_url) {
        const { data: urlMetaData, success: urlMetaDataSuccess } =
            await fetchUrlMetaDataAction(data.long_url);
        if (urlMetaData && urlMetaDataSuccess) {
            return <RedirectPage data={data} urlMetaData={urlMetaData} />;
        }
    }
    if (status === 404) {
        return <NotFound />;
    }
}
