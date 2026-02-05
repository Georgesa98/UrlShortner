"use server";

import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

interface ForgotPasswordRequest {
    email: string;
}

export async function forgotPasswordAction(data: ForgotPasswordRequest) {
    try {
        const response = await axiosInstance.post(
            "/auth/users/reset_password/",
            data
        );

        return {
            success: true,
            status: response.status,
            message: "Password reset email sent successfully",
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.detail ||
                    e.response?.data?.email?.[0] ||
                    "An error occurred while sending the reset email.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "Internal Server Error",
        };
    }
}
