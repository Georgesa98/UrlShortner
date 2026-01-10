import SpecificUrl from "./client";
import fetchUrlSummaryAction from "./server";

export default async function UrlAnalyticsPage({
    params,
    searchParams,
}: {
    params: Promise<{ id: string }>;
    searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
    const urlParams = await params;
    const range = await searchParams;
    const days = range.days ? parseInt(range.days as string, 10) : 7;
    const data = await fetchUrlSummaryAction({
        url_id: urlParams.id,
        days: days,
    });
    return <SpecificUrl data={data} />;
}
