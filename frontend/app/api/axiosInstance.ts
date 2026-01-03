import axios from "axios";
import { cookies } from "next/headers";

const axiosInstance = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_BASE_URL,
    timeout: 10000,
    headers: {
        "Content-Type": "application/json",
        withCredentials: true,
    },
});
axiosInstance.interceptors.request.use(async (config) => {
    const { cookies } = await import("next/headers");
    const cookieStore = await cookies();
    config.headers.Cookie = cookieStore.toString();
    return config;
});
export default axiosInstance;
