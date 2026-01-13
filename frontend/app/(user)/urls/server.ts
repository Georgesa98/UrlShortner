"use server";
import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function fetchUrlsAction({
    limit,
    page,
    status,
    date_order,
    query,
}: {
    limit: string;
    page: string;
    status?: string;
    date_order?: string;
    query?: string;
}) {
    const queryString = query ? `&query=${query}` : "";
    const dateOrderString = date_order ? `&date_order=${date_order}` : "";
    const statusString = status !== "ALL" ? `&url_status=${status}` : "";
    try {
        const response = await axiosInstance.get(
            `/url/?limit=${limit}&page=${page}${statusString}${dateOrderString}${queryString}`
        );
        return {
            data: response.data.data,
            status: response.status,
            success: response.data.success,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.detail ||
                    "An error occurred during signup.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "Internal Server Error",
        };
    }
}
