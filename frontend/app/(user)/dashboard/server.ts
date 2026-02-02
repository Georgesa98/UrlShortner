import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function getUserStatsAction({ days = 7 }: { days?: number }) {
  try {
    const response = await axiosInstance.get(
      `/analytics/user-stats/?days=${days}`,
    );
    return {
      success: response.data.success,
      status: response.status,
      data: response.data.data,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to get user stats",
      };
    }
    return {
      success: false,
      status: 500,
      message: "Failed to get user stats",
    };
  }
}
export async function fetchTopVisitedUrlsAction() {
  try {
    const response = await axiosInstance.get("/analytics/top-visited/");
    return {
      success: response.data.success,
      status: response.status,
      data: response.data.data,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to get top visited urls",
      };
    }
    return {
      success: false,
      status: 500,
      message: "Failed to get top visited urls",
    };
  }
}
