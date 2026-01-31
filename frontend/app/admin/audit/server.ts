import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export default async function fetchAuditLogsAction({
  page,
  limit,
  user_id,
  action,
  date_from,
  date_to,
}: {
  page: number;
  limit: number;
  user_id: string;
  action: string;
  date_from: string;
  date_to: string;
}) {
  try {
    const response = await axiosInstance.get("/admin/audit/logs/", {
      params: { page, limit, user_id, action, date_from, date_to },
    });
    return {
      success: true,
      status: response.status,
      data: response.data,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to fetch audit logs",
      };
    }
    return {
      success: false,
      status: 500,
      message: "An unexpected error occurred",
    };
  }
}
