import {
    ChartColumnIncreasing,
    Info,
    LayoutDashboard,
    Link,
    LogOut,
    Settings,
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
import { usePathname } from "next/navigation";
const sidebarItems = [
    { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
    { title: "My URLS", url: "/urls", icon: Link },
    { title: "Analytics", url: "/analytics", icon: ChartColumnIncreasing },
    { title: "Settings", url: "/settings", icon: Settings },
];
const footerSidebarItems = [
    { title: "Help Center", url: "/help", icon: Info },
    { title: "Log Out", url: "#", icon: LogOut },
];
export default function AppSidebar() {
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
                                        <Button variant="ghost">
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
