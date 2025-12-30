"use client";
import React from "react";

export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="relative overflow-hidden min-w-full h-screen">
            {/* Blue Glow (Top Left/Center) */}
            <div
                className="pointer-events-none absolute top-0 left-0 w-200 h-125 opacity-20 blur-[70px] "
                style={{
                    background:
                        "radial-gradient(circle, #007bff 0%, transparent 70%)",
                }}
            />

            {/* Purple Glow (Top Right) */}
            <div
                className="pointer-events-none absolute bottom-0 right-0 w-200 h-125 opacity-[0.15] blur-[100px]"
                style={{
                    background:
                        "radial-gradient(circle, #a855f7 0%, transparent 70%)",
                }}
            />
            <div className="relative grid place-content-center h-full">
                {children}
            </div>
        </div>
    );
}
