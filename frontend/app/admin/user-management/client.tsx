"use client";
import { useState } from "react";
import { UserResponse, Pagination } from "@/api-types";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { UserManagementDataTable } from "@/components/tables/user-management/data-table";
import { userManagementColumns } from "@/components/tables/user-management/columns";
import UserDetailsSheet from "@/components/admin-pages/UserDetailsSheet";
import { Trash2, Plus, Search, ArrowUpDown } from "lucide-react";
import { toast } from "sonner";
import { RowSelectionState } from "@tanstack/react-table";

export default function UserManagementClient({
    users,
    pagination,
}: {
    users: UserResponse[];
    pagination: Pagination;
}) {
    const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);
    const [isSheetOpen, setIsSheetOpen] = useState(false);
    const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
    const [searchQuery, setSearchQuery] = useState("");
    const [roleFilter, setRoleFilter] = useState("all");
    const [statusFilter, setStatusFilter] = useState("all");

    const handleRowClick = (user: UserResponse) => {
        setSelectedUser(user);
        setIsSheetOpen(true);
    };

    const handleBulkDelete = () => {
        const selectedCount = Object.keys(rowSelection).length;
        if (selectedCount === 0) {
            toast.error("No users selected");
            return;
        }
        toast.info(`Bulk delete ${selectedCount} users - coming soon`);
    };

    const handleAddUser = () => {
        toast.info("Add new user - coming soon");
    };

    const handlePageChange = (page: number) => {
        toast.info(`Navigate to page ${page} - coming soon`);
    };

    return (
        <div className="p-6 space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-text-main">
                        User Management
                    </h1>
                    <p className="text-text-muted mt-1">
                        Manage {pagination.total.toLocaleString()} registered
                        system users.
                    </p>
                </div>
                <div className="flex gap-3">
                    <Button
                        variant="destructive"
                        onClick={handleBulkDelete}
                        className="gap-2"
                    >
                        <Trash2 className="h-4 w-4" />
                        Bulk Delete
                    </Button>
                    <Button onClick={handleAddUser} className="gap-2">
                        <Plus className="h-4 w-4" />
                        Add New User
                    </Button>
                </div>
            </div>

            <div className="bg-surface rounded-xl p-4 flex items-center gap-4 flex-wrap">
                <div className="flex-1 min-w-[200px] relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-text-muted" />
                    <Input
                        placeholder="Search by email, username"
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-10"
                    />
                </div>
                <Select value={roleFilter} onValueChange={setRoleFilter}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="All Roles" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Roles</SelectItem>
                        <SelectItem value="user">USER</SelectItem>
                        <SelectItem value="staff">STAFF</SelectItem>
                        <SelectItem value="admin">ADMIN</SelectItem>
                    </SelectContent>
                </Select>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                    <SelectTrigger className="w-[150px]">
                        <SelectValue placeholder="All Statuses" />
                    </SelectTrigger>
                    <SelectContent>
                        <SelectItem value="all">All Statuses</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="banned">Banned</SelectItem>
                    </SelectContent>
                </Select>
                <Button variant="outline" className="gap-2">
                    <ArrowUpDown className="h-4 w-4" />
                    Sort
                </Button>
            </div>

            <UserManagementDataTable
                columns={userManagementColumns}
                data={users}
                pagination={pagination}
                onRowClick={handleRowClick}
                rowSelection={rowSelection}
                onRowSelectionChange={setRowSelection}
                onPageChange={handlePageChange}
            />

            <UserDetailsSheet
                user={selectedUser}
                isOpen={isSheetOpen}
                onClose={() => setIsSheetOpen(false)}
            />
        </div>
    );
}
