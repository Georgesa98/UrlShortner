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
    redirection_rules,
}: {
    name: string;
    long_url: string;
    short_url: string;
    expiry_date: string;
    redirection_rules?: any[];
}) {
    try {
        // First, create the URL
        const response = await axiosInstance.post("/url/shorten/", {
            name,
            long_url,
            short_url,
            expiry_date,
        });

        const urlData = response.data.data;

        // If redirection rules are provided, create them
        if (redirection_rules && redirection_rules.length > 0) {
            try {
                const rulesPayload = {
                    rules: redirection_rules.map((rule) => ({
                        name: rule.name,
                        url_id: urlData.id,
                        conditions: rule.conditions || {},
                        target_url: rule.target_url,
                        priority: rule.priority,
                        is_active: rule.is_active,
                    })),
                };

                await axiosInstance.post(
                    "/url/redirection/rules/batch/",
                    rulesPayload
                );
            } catch (rulesError) {
                // Log the error but don't fail the URL creation
                console.error("Failed to create redirection rules:", rulesError);
                // Optionally show a warning toast
            }
        }

        return {
            data: urlData,
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

export async function updateShortUrlAction({
    short_url,
    name,
    long_url,
    expiry_date,
    redirection_rules,
}: {
    short_url: string;
    name: string;
    long_url: string;
    expiry_date: string;
    redirection_rules?: any[];
}) {
    try {
        // Update the URL
        const response = await axiosInstance.patch(`/url/${short_url}/`, {
            name,
            long_url,
            expiry_date,
        });

        const urlData = response.data.data;

        // Handle redirection rules updates
        if (redirection_rules !== undefined) {
            try {
                // First, delete existing rules for this URL
                await axiosInstance.delete(
                    `/url/redirection/rules/?url_id=${urlData.id}`
                );

                // Then, create new rules if any are provided
                if (redirection_rules.length > 0) {
                    const rulesPayload = {
                        rules: redirection_rules.map((rule) => ({
                            name: rule.name,
                            url_id: urlData.id,
                            conditions: rule.conditions || {},
                            target_url: rule.target_url,
                            priority: rule.priority,
                            is_active: rule.is_active,
                        })),
                    };

                    await axiosInstance.post(
                        "/url/redirection/rules/batch/",
                        rulesPayload
                    );
                }
            } catch (rulesError) {
                // Log the error but don't fail the URL update
                console.error("Failed to update redirection rules:", rulesError);
            }
        }

        return {
            data: urlData,
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
                    "An error occurred during url update.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An error occurred during url update.",
        };
    }
}

export async function fetchRedirectionRulesAction(urlId: number) {
    try {
        const response = await axiosInstance.get(
            `/url/redirection/rules/?url_id=${urlId}`
        );
        return {
            data: response.data.data || [],
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
                    "An error occurred during fetching redirection rules.",
                data: [],
            };
        }
        return {
            success: false,
            status: 500,
            message: "An error occurred during fetching redirection rules.",
            data: [],
        };
    }
}
