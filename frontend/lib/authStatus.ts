"use server";

import { cookies } from "next/headers";
import { jwtVerify } from "jose";

export async function getAuthStatus() {
    try {
        const SECRET = new TextEncoder().encode(process.env.JWT_SECRET);
        const cookieStore = await cookies();
        const token = cookieStore.get("access_token")?.value;
        if (!token) return { isLoggedIn: false, isAdmin: false };

        const { payload } = await jwtVerify(token, SECRET);

        return {
            isLoggedIn: true,
            isAdmin: payload.role === "admin",
            user: payload.sub,
        };
    } catch (error) {
        console.error(error);

        return { isLoggedIn: false, isAdmin: false };
    }
}
