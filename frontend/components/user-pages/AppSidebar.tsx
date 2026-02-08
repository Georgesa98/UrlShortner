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
import { usePathname, useRouter } from "next/navigation";
import axiosClient from "@/app/api/axiosClient";
import { toast } from "sonner";
import { cn } from "@/lib/utils";
const sidebarItems = [
  { title: "Dashboard", url: "/dashboard", icon: LayoutDashboard },
  { title: "My URLS", url: "/urls", icon: Link },
  { title: "Settings", url: "/settings", icon: Settings },
];
const footerSidebarItems = [
  { action: "logout", title: "Log Out", url: "#", icon: LogOut },
];
export default function AppSidebar() {
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
      <SidebarContent className="px-3">
        <SidebarMenu className="gap-0">
          {sidebarItems.map((item) => {
            return (
              <SidebarMenuItem key={item.title}>
                <SidebarMenuButton
                  asChild
                  isActive={pathname === item.url}
                  className={cn(
                    "h-14",
                    pathname === item.url &&
                      "bg-blue-600! hover:bg-blue-700! text-white! shadow-lg shadow-blue-500/50"
                  )}
                >
                  <NavLink href={item.url} className="flex items-center gap-2">
                    <item.icon />
                    <span>{item.title}</span>
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
                  <NavLink
                    href={item.url}
                    className="flex items-center gap-2"
                    onClick={() => {
                      if (item.action === "logout") {
                        logout();
                      }
                    }}
                  >
                    <item.icon />
                    <span>{item.title}</span>
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
