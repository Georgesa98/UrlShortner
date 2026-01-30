"use server";

import FraudDetectionOverview from "./client";
import { fetchFraudOverviewAction, fetchIncidentsAction } from "./server";

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
  const { data } = await fetchFraudOverviewAction();
  const { data: incidentsTableData } = await fetchIncidentsAction({
    page: parseInt(page),
    limit: parseInt(limit),
  });
  return (
    <FraudDetectionOverview
      data={data}
      incidentsTableData={incidentsTableData}
    />
  );
}
