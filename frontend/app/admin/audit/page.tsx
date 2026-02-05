"use server";

import AuditLogsClient from "./client";
import fetchAuditLogsAction from "./server";

// Helper function to convert timestamp to YYYY-MM-DD format
function formatDateForBackend(timestamp: string): string {
  if (!timestamp) return "";
  try {
    const date = new Date(parseInt(timestamp));
    return date.toISOString().split("T")[0]; // Returns YYYY-MM-DD
  } catch {
    return "";
  }
}

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
    date_from: formatDateForBackend(params.date_from),
    date_to: formatDateForBackend(params.date_to),
  });

  return <AuditLogsClient logs={logs.data} />;
}
