"use server";
import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function listUrlsAction({
  page = 1,
  limit = 10,
  query = "",
  url_status,
  date_order,
}: {
  page?: number;
  limit?: number;
  query?: string;
  url_status?: string;
  date_order?: string;
}) {
  try {
    const response = await axiosInstance.get("/admin/url/", {
      params: { page, limit, query, url_status, date_order },
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
        message: e.response?.data?.message || "Failed to fetch URLs",
      };
    }
    return {
      success: false,
      status: 500,
      message: "An unexpected error occurred",
    };
  }
}

export async function platformStatsAction() {
  try {
    const response = await axiosInstance.get("/admin/url/stats/");
    return {
      success: true,
      status: response.status,
      data: response.data.data,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to fetch stats",
      };
    }
    return {
      success: false,
      status: 500,
      message: "An unexpected error occurred",
    };
  }
}

export async function bulkDeleteUrlsAction({ url_ids }: { url_ids: number[] }) {
  try {
    const response = await axiosInstance.post("/admin/url/bulk-delete/", {
      url_ids,
    });
    return {
      success: true,
      status: response.status,
      message: response.data.message || "URLs deleted successfully",
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to delete URLs",
      };
    }
    return {
      success: false,
      status: 500,
      message: "An unexpected error occurred",
    };
  }
}
