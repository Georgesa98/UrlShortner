"use server";

import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";
import { SetPasswordRequest, UpdateUserProfileRequest } from "@/api-types";

export async function getUserProfileAction() {
  try {
    const response = await axiosInstance.get("/auth/users/me/");
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
        message: e.response?.data?.message || "Failed to get user profile",
      };
    }
    return {
      success: false,
      status: 500,
      message: "Failed to get user profile",
    };
  }
}

export async function updateUserProfileAction(data: UpdateUserProfileRequest) {
  try {
    const response = await axiosInstance.patch("/auth/users/me/", data);
    return {
      success: true,
      status: response.status,
      data: response.data,
      message: "Profile updated successfully",
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to update profile",
      };
    }
    return {
      success: false,
      status: 500,
      message: "Failed to update profile",
    };
  }
}

export async function setPasswordAction(data: SetPasswordRequest) {
  try {
    const response = await axiosInstance.post("/auth/users/set_password/", data);
    return {
      success: true,
      status: response.status,
      message: "Password updated successfully",
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to update password",
      };
    }
    return {
      success: false,
      status: 500,
      message: "Failed to update password",
    };
  }
}

export async function deleteAccountAction() {
  try {
    const response = await axiosInstance.delete("/auth/users/me/");
    return {
      success: true,
      status: response.status,
      message: "Account deleted successfully",
    };
  } catch (e: unknown) {
    if (e instanceof AxiosError) {
      return {
        success: false,
        status: e.response?.status || 500,
        message: e.response?.data?.message || "Failed to delete account",
      };
    }
    return {
      success: false,
      status: 500,
      message: "Failed to delete account",
    };
  }
}
