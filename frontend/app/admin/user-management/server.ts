"use server";
import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function fetchUsersAction({
    page,
    limit,
    query,
    roles,
    is_active,
    order_by,
}: {
    page: number;
    limit: number;
    query: string;
    roles: string;
    is_active: string;
    order_by: string;
}) {
    try {
        const response = await axiosInstance.get(
            `/admin/user/?page=${page}&limit=${limit}&query=${query}&roles=${roles}&is_active=${is_active}&order_by=${order_by}`
        );
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
                message: e.response?.data?.message || "Failed to fetch users",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
export async function bulkDeleteUsersAction({
    user_ids,
}: {
    user_ids: number[];
}) {
    try {
        const response = await axiosInstance.post("/admin/user/bulk-delete/", {
            user_ids,
        });
        return {
            success: true,
            status: response.status,
            message: response.data.message,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.message || "Failed to bulk delete users",
            };
        }

        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
export async function toggleBanUserAction({ user_id }: { user_id: number }) {
    try {
        const response = await axiosInstance.patch(
            `/admin/user/${user_id}/ban/`
        );
        return {
            success: true,
            status: response.status,
            message: response.data.message,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.message || "Failed to toggle ban user",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
export async function getUserUrlsAction({ user_id }: { user_id: number }) {
    try {
        const response = await axiosInstance.get(
            `/admin/user/${user_id}/urls/`
        );
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
                message: e.response?.data?.message || "Failed to get user urls",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
