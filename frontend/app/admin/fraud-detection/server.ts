import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function fetchFraudOverviewAction() {
  try {
    const response = await axiosInstance.get("/admin/fraud/overview/");
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
        message: e.response?.data?.message || "Failed to fetch fraud overview",
      };
    }
    return {
      success: false,
      status: 500,
      message: "Failed to fetch fraud overview",
    };
  }
}
export async function fetchIncidentsAction({
  page,
  limit,
}: {
  page: number;
  limit: number;
}) {
  try {
    const response = await axiosInstance.get(
      `/admin/url?limit=${limit}&page=${page}&url_status=FLAGGED`,
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
        message: e.response?.data?.message || "Failed to fetch incidents",
      };
    }
  }
  return {
    success: false,
    status: 500,
    message: "Failed to fetch incidents",
  };
}
