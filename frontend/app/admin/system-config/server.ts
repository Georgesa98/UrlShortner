"use server";

import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export interface SystemConfig {
  key: string;
  value: string;
  description?: string;
  updated_at?: string;
}

export async function getSystemConfigsAction() {
  try {
    const response = await axiosInstance.get("/admin/system/config/");
    return {
      success: response.data.success,
      status: response.status,
      data: response.data.data,
      message: response.data.message,
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message:
          e.response?.data?.message ||
          "An error occurred while fetching system configurations.",
      };
    }
    return {
      success: false,
      status: 500,
      message: "An error occurred while fetching system configurations.",
    };
  }
}

export async function updateSystemConfigsAction(
  configs: Record<string, string | number | boolean>
) {
  try {
    // Convert all values to strings for the backend
    const configsPayload: Record<string, string> = {};
    for (const [key, value] of Object.entries(configs)) {
      if (typeof value === "boolean") {
        configsPayload[key] = value ? "true" : "false";
      } else {
        configsPayload[key] = String(value);
      }
    }

    const response = await axiosInstance.post("/admin/system/config/batch/", {
      configs: configsPayload,
    });

    return {
      success: response.data.success,
      status: response.status,
      data: response.data.data,
      message: response.data.message || "Configurations updated successfully",
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message:
          e.response?.data?.message ||
          "An error occurred while updating system configurations.",
        errors: e.response?.data?.errors,
      };
    }
    return {
      success: false,
      status: 500,
      message: "An error occurred while updating system configurations.",
    };
  }
}
