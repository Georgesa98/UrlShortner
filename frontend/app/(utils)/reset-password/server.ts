"use server";

import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

interface ResetPasswordConfirmRequest {
    uid: string;
    token: string;
    new_password: string;
    re_new_password: string;
}

export async function resetPasswordAction(data: ResetPasswordConfirmRequest) {
    try {
        const response = await axiosInstance.post(
            "/auth/users/reset_password_confirm/",
            data
        );

        return {
            success: true,
            status: response.status,
            message: "Password has been reset successfully",
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.detail ||
                    e.response?.data?.token?.[0] ||
                    e.response?.data?.uid?.[0] ||
                    e.response?.data?.new_password?.[0] ||
                    "An error occurred while resetting your password.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "Internal Server Error",
        };
    }
}
