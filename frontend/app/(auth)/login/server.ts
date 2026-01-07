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
                const parts = cookieString
                    .split(";")
                    .map((part) => part.trim());
                const [nameValue] = parts;
                const [name, value] = nameValue.split("=");

                const attributes: any = {
                    httpOnly: false,
                    secure: false,
                    sameSite: "lax" as const,
                    path: "/",
                };

                parts.slice(1).forEach((part) => {
                    const [key, val] = part.split("=").map((s) => s.trim());
                    const lowerKey = key.toLowerCase();

                    if (lowerKey === "httponly") {
                        attributes.httpOnly = true;
                    } else if (lowerKey === "secure") {
                        attributes.secure = true;
                    } else if (lowerKey === "samesite") {
                        attributes.sameSite = val.toLowerCase();
                    } else if (lowerKey === "path") {
                        attributes.path = val;
                    } else if (lowerKey === "max-age") {
                        attributes.maxAge = parseInt(val, 10);
                    } else if (lowerKey === "expires") {
                        attributes.expires = new Date(val);
                    } else if (lowerKey === "domain") {
                        attributes.domain = val;
                    }
                });

                cookieStore.set(name.trim(), value.trim(), attributes);
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
