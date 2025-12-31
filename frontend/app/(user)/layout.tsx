"use client";
import { SidebarProvider } from "@/components/ui/sidebar";
import AppSidebar from "@/components/user-pages/AppSidebar";
import React from "react";

export default function UserLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <SidebarProvider>
            <AppSidebar />
            <div>{children}</div>
        </SidebarProvider>
    );
}
