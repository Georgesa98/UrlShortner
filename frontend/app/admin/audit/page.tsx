"use server";

import AuditLogsClient from "./client";
import fetchAuditLogsAction from "./server";

export default async function Page({
  searchParams,
}: {
  searchParams: {
    page: string;
    limit: string;
    user_id: string;
    action: string;
    date_from: string;
    date_to: string;
  };
}) {
  const params = await searchParams;
  const { data: logs } = await fetchAuditLogsAction({
    page: parseInt(params.page) || 1,
    limit: parseInt(params.limit) || 10,
    user_id: params.user_id || "",
    action: params.action || "",
    date_from: params.date_from || "",
    date_to: params.date_to || "",
  });

  return <AuditLogsClient logs={logs.data} />;
}
