"use client";

import Navbar from "@/components/landing-page/Navbar";
import { ReactNode } from "react";

export default function Layout({ children }: { children: ReactNode }) {
    return (
        <div className="relative overflow-hidden">
            {/* Blue Glow (Top Left/Center) */}
            <div
                className="pointer-events-none absolute -top-25 -left-[20%] w-200 h-125 opacity-20 blur-[70px] "
                style={{
                    background:
                        "radial-gradient(circle, #007bff 0%, transparent 70%)",
                }}
            />

            {/* Purple Glow (Top Right) */}
            <div
                className="pointer-events-none absolute top-30 -right-[14%] w-150 h-125 opacity-[0.15] blur-[100px]"
                style={{
                    background:
                        "radial-gradient(circle, #a855f7 0%, transparent 70%)",
                }}
            />
            <div className="relative">
                <Navbar />
                <div className="container min-w-full">{children}</div>
            </div>
        </div>
    );
}
