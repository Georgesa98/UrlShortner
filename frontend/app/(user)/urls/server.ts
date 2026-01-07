import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function fetchUrls({
    limit,
    page,
}: {
    limit: string;
    page: string;
}) {
    try {
        const response = await axiosInstance.get(
            `/url/?limit=${limit}&page=${page}`
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
