import axiosInstance from "@/app/api/axiosInstance";
import { extractOpenGraph } from "@devmehq/open-graph-extractor";
import axios, { AxiosError } from "axios";

export async function fetchUrlAction(short_url: string) {
    try {
        console.log(short_url);
        const response = await axiosInstance.get(`/url/${short_url}/`);
        if (response.data.success) {
            return response.data;
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

export async function fetchUrlMetaDataAction(long_url: string) {
    try {
        const { data: html } = await axios.get(long_url);
        const urlMetaData = await extractOpenGraph(html);
        return {
            success: true,
            data: urlMetaData,
            status: 200,
        };
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
