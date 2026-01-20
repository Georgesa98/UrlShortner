import {
    ChartColumnIncreasing,
    FileText,
    Info,
    LayoutDashboard,
    Link,
    LogOut,
    Settings,
    ShieldAlert,
    Users,
} from "lucide-react";
import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarHeader,
    SidebarMenu,
    SidebarMenuButton,
    SidebarMenuItem,
} from "../ui/sidebar";
import NavLink from "next/link";
import { Button } from "../ui/button";
import { usePathname, useRouter } from "next/navigation";
import axiosClient from "@/app/api/axiosClient";
import { toast } from "sonner";
const sidebarItems = [
    { title: "Dashboard", url: "/admin/dashboard", icon: LayoutDashboard },
    { title: "Url Management", url: "/admin/urls-management", icon: Link },
    { title: "User Management", url: "/admin/users", icon: Users },
    {
        title: "Fraud Detection",
        url: "/admin/fraud-detection",
        icon: ShieldAlert,
    },
    { title: "Audit Logs", url: "/admin/audit-logs", icon: FileText },
];
const footerSidebarItems = [
    { action: "logout", title: "Log Out", url: "#", icon: LogOut },
];
export default function AdminSidebar() {
    const router = useRouter();
    async function logout() {
        const response = await axiosClient.post("/auth/logout/");
        if (response.status === 200) {
            toast.success("logged out successfully");
            router.push("/login");
        } else {
            toast.error("error has occurred");
        }
    }
    const pathname = usePathname();
    return (
        <Sidebar>
            <SidebarHeader />
            <SidebarContent>
                <SidebarMenu className="gap-0">
                    {sidebarItems.map((item) => {
                        return (
                            <SidebarMenuItem key={item.title}>
                                <SidebarMenuButton asChild className="h-14">
                                    <NavLink href={item.url}>
                                        <Button
                                            className={`w-full justify-start gap-2 h-10`}
                                            variant={
                                                pathname === item.url
                                                    ? "default"
                                                    : "ghost"
                                            }
                                        >
                                            <item.icon />
                                            <span>{item.title}</span>
                                        </Button>
                                    </NavLink>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        );
                    })}
                </SidebarMenu>
            </SidebarContent>
            <SidebarFooter>
                <SidebarMenu>
                    {footerSidebarItems.map((item) => {
                        return (
                            <SidebarMenuItem key={item.title}>
                                <SidebarMenuButton asChild>
                                    <NavLink href={item.url}>
                                        <Button
                                            onClick={() => {
                                                if (item.action === "logout") {
                                                    console.log("asd");

                                                    logout();
                                                }
                                            }}
                                            variant="ghost"
                                        >
                                            <item.icon />
                                            <span>{item.title}</span>
                                        </Button>
                                    </NavLink>
                                </SidebarMenuButton>
                            </SidebarMenuItem>
                        );
                    })}
                </SidebarMenu>
            </SidebarFooter>
        </Sidebar>
    );
}
