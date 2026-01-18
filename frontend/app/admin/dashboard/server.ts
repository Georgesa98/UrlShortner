import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function platformStatsAction({
    time_range,
}: {
    time_range: string;
}) {
    try {
        const response = await axiosInstance.get(
            `/admin/insight/platform-stats/?time_range=${time_range}`
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

export async function growthMetricsAction() {
    try {
        const response = await axiosInstance.get(
            `/admin/insight/growth-metric/`
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

export async function topPerformersAction({
    metric,
    limit,
}: {
    metric: string;
    limit: number;
}) {
    try {
        const response = await axiosInstance.get(
            `/admin/insight/top-performers/?metric=${metric}&limit=${limit}`
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
                message:
                    e.response?.data?.message ||
                    "An error occurred during fetching top performers.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An error occurred during fetching top performers.",
        };
    }
}

export async function peakTimesAction() {
    try {
        const response = await axiosInstance.get(`/admin/insight/peak-times/`);
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
                message:
                    e.response?.data?.message ||
                    "An error occurred during fetching peak times.",
            };
        }

        return {
            success: false,
            status: 500,
            message: "An error occurred during fetching peak times.",
        };
    }
}

export async function geoDistributionAction() {
    try {
        const response = await axiosInstance.get(`/admin/insight/geo-dist/`);
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
                message:
                    e.response?.data?.message ||
                    "An error occurred during fetching geo distribution.",
            };
        }
    }
    return {
        success: false,
        status: 500,
        message: "An error occurred during fetching geo distribution.",
    };
}

export async function systemHealthAction() {
    try {
        const response = await axiosInstance.get(`/admin/system/health/`);
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
                message:
                    e.response?.data?.message ||
                    "An error occurred during fetching system health.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An error occurred during fetching system health.",
        };
    }
}
