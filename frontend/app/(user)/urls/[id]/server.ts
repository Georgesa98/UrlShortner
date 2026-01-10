import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export default async function fetchUrlSummaryAction({
    url_id,
    days,
}: {
    url_id: string;
    days: number;
}) {
    try {
        const response = await axiosInstance.get(
            `/analytics/url-summary/${url_id}?days=${days}`
        );
        if (response.data.success) {
            return response.data.data;
        }
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data || "An error occurred during fetching.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "Internal Server Error",
        };
    }
}
