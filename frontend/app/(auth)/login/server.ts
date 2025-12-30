"use server";

import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";
import { LoginRequest } from "@/api-types";
import { cookies } from "next/headers";
export async function loginAction(data: LoginRequest) {
    try {
        const response = await axiosInstance.post("/auth/jwt/create/", data);
        const djangoCookies = response.headers["set-cookie"];
        if (djangoCookies) {
            const cookieStore = await cookies();
            djangoCookies.forEach((cookieString) => {
                const [nameValue] = cookieString.split(";");
                const [name, value] = nameValue.split("=");
                cookieStore.set(name.trim(), value.trim(), {
                    httpOnly: true,
                    secure: process.env.NODE_ENV === "production",
                    sameSite: "lax",
                    path: "/",
                });
            });
        }

        return {
            success: true,
            data: response.data,
            status: response.status,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.detail ||
                    "An error occurred during login.",
            };
        }
        return {
            success: false,
            status: 500,
            message: "Internal Server Error",
        };
    }
}
