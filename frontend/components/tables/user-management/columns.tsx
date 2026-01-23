"use client";
import { UserResponse } from "@/api-types";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";

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

export const userManagementColumns: ColumnDef<UserResponse>[] = [
    {
        id: "select",
        header: ({ table }) => (
            <Checkbox
                checked={table.getIsAllPageRowsSelected()}
                onCheckedChange={(value) =>
                    table.toggleAllPageRowsSelected(!!value)
                }
                aria-label="Select all"
                className="translate-y-[2px]"
            />
        ),
        cell: ({ row }) => (
            <Checkbox
                checked={row.getIsSelected()}
                onCheckedChange={(value) => row.toggleSelected(!!value)}
                aria-label="Select row"
                className="translate-y-[2px]"
                onClick={(e) => e.stopPropagation()}
            />
        ),
        enableSorting: false,
        enableHiding: false,
    },
    {
        accessorKey: "user",
        header: "User",
        cell: ({ row }) => {
            const data = row.original;
            const initials = `${data.first_name?.[0] || ""}${data.last_name?.[0] || ""}`.toUpperCase() || data.username.substring(0, 2).toUpperCase();
            
            return (
                <div className="flex items-center gap-3 px-6">
                    <div className="w-10 h-10 rounded-full bg-brand-blue/20 flex items-center justify-center text-brand-blue font-semibold">
                        {initials}
                    </div>
                    <div className="flex flex-col">
                        <span className="text-text-main font-medium">
                            {data.first_name && data.last_name
                                ? `${data.first_name} ${data.last_name}`
                                : data.username}
                        </span>
                        <span className="text-text-muted text-sm">
                            {data.username}
                        </span>
                    </div>
                </div>
            );
        },
    },
    {
        accessorKey: "status",
        header: "Status",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <Badge variant={getStatusBadgeVariant(data.is_active)}>
                    {data.is_active ? "Active" : "Banned"}
                </Badge>
            );
        },
    },
    {
        accessorKey: "role",
        header: "Role",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <Badge variant={getRoleBadgeVariant(data.role)}>
                    {data.role}
                </Badge>
            );
        },
    },
];
