"use client";
import { UserResponse } from "@/api-types";
import {
    Sheet,
    SheetContent,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { toast } from "sonner";

interface UserDetailsSheetProps {
    user: UserResponse | null;
    isOpen: boolean;
    onClose: () => void;
}

export default function UserDetailsSheet({
    user,
    isOpen,
    onClose,
}: UserDetailsSheetProps) {
    const [accountAccessEnabled, setAccountAccessEnabled] = useState(
        user?.is_active ?? true
    );

    if (!user) return null;

    const initials = `${user.first_name?.[0] || ""}${user.last_name?.[0] || ""}`.toUpperCase() || user.username.substring(0, 2).toUpperCase();

    const handleToggleAccountAccess = () => {
        setAccountAccessEnabled(!accountAccessEnabled);
        toast.success(
            accountAccessEnabled
                ? "User account access restricted"
                : "User account access restored"
        );
    };

    const handleEditProfile = () => {
        toast.info("Edit profile functionality coming soon");
    };

    const handleLoginAsUser = () => {
        toast.info("Login as user functionality coming soon");
    };

    const getRoleBadgeVariant = (role: string) => {
        switch (role) {
            case "ADMIN":
                return "default";
            case "STAFF":
                return "secondary";
            default:
                return "outline";
        }
    };

    const getStatusBadgeVariant = (isActive: boolean) => {
        return isActive ? "success" : "destructive";
    };

    return (
        <Sheet open={isOpen} onOpenChange={onClose}>
            <SheetContent className="bg-background w-full sm:max-w-md overflow-y-auto">
                <SheetHeader className="border-b border-border-subtle pb-4">
                    <SheetTitle className="text-text-main text-xl">
                        User Details
                    </SheetTitle>
                </SheetHeader>

                <div className="space-y-6 py-6">
                    <div className="flex flex-col items-center gap-4 pb-6 border-b border-border-subtle">
                        <div className="w-24 h-24 rounded-full bg-brand-blue/20 flex items-center justify-center text-brand-blue font-bold text-2xl">
                            {initials}
                        </div>
                        <div className="text-center">
                            <h2 className="text-text-main font-semibold text-lg">
                                {user.first_name && user.last_name
                                    ? `${user.first_name} ${user.last_name}`
                                    : user.username}
                            </h2>
                            <p className="text-text-muted text-sm">
                                {user.username}
                            </p>
                        </div>
                        <div className="flex gap-2">
                            <Badge variant={getRoleBadgeVariant(user.role)}>
                                {user.role}
                            </Badge>
                            <Badge variant={getStatusBadgeVariant(user.is_active)}>
                                {user.is_active ? "ACTIVE" : "BANNED"}
                            </Badge>
                        </div>
                    </div>

                    <div className="space-y-4">
                        <div className="flex items-center justify-between py-3 border-b border-border-subtle">
                            <span className="text-text-muted text-sm">
                                Account Access
                            </span>
                            <label className="relative inline-flex items-center cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={accountAccessEnabled}
                                    onChange={handleToggleAccountAccess}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-ring rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-blue"></div>
                            </label>
                        </div>
                    </div>

                    <div className="space-y-3">
                        <div className="flex justify-between items-center">
                            <span className="text-text-muted text-sm uppercase tracking-wider">
                                User ID
                            </span>
                            <span className="text-text-main font-mono">
                                usr_{user.id.toString().padStart(8, "0")}
                            </span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-text-muted text-sm uppercase tracking-wider">
                                Date Joined
                            </span>
                            <span className="text-text-main">
                                {new Date(user.date_joined).toLocaleDateString(
                                    "en-US",
                                    {
                                        month: "short",
                                        day: "numeric",
                                        year: "numeric",
                                    }
                                )}
                            </span>
                        </div>
                        <div className="flex justify-between items-center">
                            <span className="text-text-muted text-sm uppercase tracking-wider">
                                Email Address
                            </span>
                            <span className="text-text-main">{user.email}</span>
                        </div>
                    </div>

                    <div className="pt-6 border-t border-border-subtle">
                        <div className="flex justify-between items-center mb-4">
                            <h3 className="text-text-main font-semibold">
                                User Links
                            </h3>
                            <span className="text-text-muted text-sm">
                                142 Total
                            </span>
                        </div>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between p-3 bg-surface-hover rounded-lg">
                                <div className="flex-1">
                                    <div className="text-text-main font-medium text-sm">
                                        Promo 2024
                                    </div>
                                    <div className="text-text-muted text-xs truncate">
                                        github.com/...
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-text-main font-semibold">
                                        1.2k
                                    </div>
                                    <div className="text-text-muted text-xs">
                                        12d
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-surface-hover rounded-lg">
                                <div className="flex-1">
                                    <div className="text-text-main font-medium text-sm">
                                        Bio Link
                                    </div>
                                    <div className="text-text-muted text-xs truncate">
                                        linkedin.com/...
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-text-main font-semibold">
                                        842
                                    </div>
                                    <div className="text-brand-blue text-xs">
                                        ∞
                                    </div>
                                </div>
                            </div>
                            <div className="flex items-center justify-between p-3 bg-surface-hover rounded-lg">
                                <div className="flex-1">
                                    <div className="text-text-main font-medium text-sm">
                                        Waitlist
                                    </div>
                                    <div className="text-text-muted text-xs truncate">
                                        tally.so/r/n2...
                                    </div>
                                </div>
                                <div className="text-right">
                                    <div className="text-text-main font-semibold">
                                        3.4k
                                    </div>
                                    <div className="text-text-muted text-xs">
                                        Exp.
                                    </div>
                                </div>
                            </div>
                        </div>
                        <button className="w-full mt-4 text-brand-blue text-sm font-medium hover:underline">
                            View all user links
                        </button>
                    </div>

                    <div className="pt-6 border-t border-border-subtle space-y-3">
                        <Button
                            variant="outline"
                            className="w-full"
                            onClick={handleEditProfile}
                        >
                            Edit Profile
                        </Button>
                        <Button
                            variant="default"
                            className="w-full"
                            onClick={handleLoginAsUser}
                        >
                            Login as User
                        </Button>
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    );
}
