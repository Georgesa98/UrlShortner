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
    try {
        const cookiesStore = await cookies();
        const allCookies = cookiesStore.toString();
        if (allCookies) {
            config.headers.Cookie = allCookies;
        }
    } catch (err) {
        console.warn("Axios-Server: No request context found for cookies.");
    }
    return config;
});
export default axiosInstance;
