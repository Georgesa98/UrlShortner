"use server";
import axiosInstance from "@/app/api/axiosInstance";
import { AxiosResponse } from "axios";
export async function signupAction(
    email: string,
    username: string,
    password: string
) {
    try {
        const response: AxiosResponse = await axiosInstance.post(
            "/auth/users/",
            {
                email,
                username,
                password,
            }
        );
        return { data: response.data, status: response.status };
    } catch (e) {
        return { error: e.message };
    }
}
