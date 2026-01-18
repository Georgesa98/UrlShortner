import { NextRequest, NextResponse } from "next/server";
import axiosInstance from "./app/api/axiosInstance";
import { jwtVerify } from "jose";
const SECRET_KEY = new TextEncoder().encode(process.env.JWT_SECRET);
export default async function proxy(request: NextRequest) {
    const { pathname } = request.nextUrl;
    const excludedPaths = ["/", "/login", "/register", "/redirect"];
    const isExcluded = excludedPaths.some(
        (path) => pathname === path || pathname.startsWith(`${path}/`)
    );
    if (request.headers.get("purpose") === "prefetch" || isExcluded) {
        return NextResponse.next();
    }
    const accessToken = request.cookies.get("access_token")?.value;
    const refreshToken = request.cookies.get("refresh_token")?.value;

    if (!refreshToken && !request.nextUrl.pathname.startsWith("/login")) {
        return NextResponse.redirect(new URL("/login", request.url));
    }
    if (!accessToken && refreshToken) {
        try {
            const response = await axiosInstance.post("/auth/jwt/refresh/", {
                refresh: refreshToken,
            });

            if (response.status === 200) {
                const data = await response.data;
                const newAccessToken = data.access;
                const res = NextResponse.next();
                if (newAccessToken) {
                    res.cookies.set("access_token", newAccessToken, {
                        httpOnly: true,
                        secure: process.env.NODE_ENV === "production",
                        sameSite: "lax",
                        path: "/",
                        maxAge: 60 * 5,
                    });
                    request.cookies.set("access_token", newAccessToken);
                }
                return res;
            }
        } catch (error) {
            return NextResponse.redirect(new URL("/login", request.url));
        }
    }

    if (pathname.startsWith("/admin")) {
        if (!accessToken) {
            return NextResponse.redirect(new URL("/login", request.url));
        }
        try {
            const { payload } = await jwtVerify(accessToken, SECRET_KEY);
            if (payload.role !== "ADMIN") {
                return NextResponse.redirect(new URL("/404", request.url));
            }
        } catch (error) {
            console.error("JWT Verification failed:", error);
            return NextResponse.redirect(new URL("/login", request.url));
        }
    }
    return NextResponse.next();
}
export const config = {
    matcher: [
        /*
         * 1. Match all paths except for:
         * - api (internal routes)
         * - _next/static (static files)
         * - _next/image (image optimization)
         * - favicon.ico, sitemap.xml, robots.txt (metadata)
         */
        "/((?!api|_next/static|_next/image|favicon.ico|.*\\.png$|.*\\.jpg$|.*\\.svg$).*)",
    ],
};
