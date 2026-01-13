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
                    e.response?.data?.message ||
                    "An error occurred during fetching urls.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An error occurred during fetching urls.",
        };
    }
}
export async function createShortUrlAction({
    name,
    long_url,
    short_url,
    expiry_date,
}: {
    name: string;
    long_url: string;
    short_url: string;
    expiry_date: string;
}) {
    try {
        const response = await axiosInstance.post("/url/shorten/", {
            name,
            long_url,
            short_url,
            expiry_date,
        });
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
                    e.response?.data?.message ||
                    "An error occurred during url shortening.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An error occurred during url shortening.",
        };
    }
}

export async function batchShortenUrlAction({
    data,
}: {
    data: Record<string, any>[];
}) {
    try {
        const response = await axiosInstance.post("/url/batch-shorten/", data);
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
                    e.response?.data?.message ||
                    "An error occurred during batch url shortening.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An error occurred during batch url shortening.",
        };
    }
}
