"use client";

import AdminSidebar from "@/components/admin-pages/AdminSidebar";
import { SidebarProvider } from "@/components/ui/sidebar";

export default function AdminLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <SidebarProvider>
            <AdminSidebar />
            <div className="p-6 w-full">{children}</div>
        </SidebarProvider>
    );
}
