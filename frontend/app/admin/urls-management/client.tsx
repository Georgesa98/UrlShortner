"use client";

import { useEffect, useRef, useState } from "react";
import { UrlResponse, Pagination } from "@/api-types";
import UrlStatCards from "@/components/admin/urls-management/UrlStatCards";
import UrlManagementHeader from "@/components/admin/urls-management/UrlManagementHeader";
import { AdminUrlDataTable } from "@/components/tables/admin-url/data-table";
import { adminUrlColumns } from "@/components/tables/admin-url/columns";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { RowSelectionState } from "@tanstack/react-table";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import { toast } from "sonner";
import { DeleteUrlDialog } from "@/components/dialogs/DeleteUrlDialog";
import { bulkDeleteUrlsAction } from "./server";

export default function UrlsManagementPage({
  urls,
  stats,
  pagination,
}: {
  urls: UrlResponse[];
  stats: Record<string, number>;
  pagination: Pagination;
}) {
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const searchParam = useSearchParams();
  const [searchQuery, setSearchQuery] = useState(
    searchParam.get("query") || "",
  );
  const isInitialMount = useRef(true);
  const previousSearchValue = useRef(searchQuery);

  const handleBulkDelete = () => {
    const selectedUrlIds = Object.keys(rowSelection).map((id) => parseInt(id));
    if (selectedUrlIds.length === 0) {
      toast.error("No URLs selected");
      return;
    }
    setIsDeleteDialogOpen(true);
  };

  const handleStatusChange = (newStatus: string) => {
    const params = new URLSearchParams(searchParam.toString());
    if (newStatus === "ALL") {
      params.delete("url_status");
    } else {
      params.set("url_status", newStatus);
    }
    params.set("page", "1");
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  };

  const handleDateOrderChange = (newOrder: string) => {
    const params = new URLSearchParams(searchParam.toString());
    if (newOrder === "DEFAULT") {
      params.delete("date_order");
    } else {
      params.set("date_order", newOrder);
    }
    params.set("page", "1");
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  };

  const confirmBulkDelete = async () => {
    const selectedUrlIds = Object.keys(rowSelection).map((id) => parseInt(id));
    setIsDeleting(true);
    try {
      const response = await bulkDeleteUrlsAction({ url_ids: selectedUrlIds });

      if (response.success) {
        toast.success(
          `Deleted ${selectedUrlIds.length} URL${selectedUrlIds.length > 1 ? "s" : ""} successfully`,
        );
        setRowSelection({});
        router.refresh();
      } else {
        toast.error(response.message);
      }
    } catch (error) {
      toast.error("Failed to delete URLs");
    } finally {
      setIsDeleting(false);
      setIsDeleteDialogOpen(false);
    }
  };

  function handlePageChange(newPage: number) {
    const params = new URLSearchParams(searchParam.toString());
    params.set("page", newPage.toString());
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  }
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
      previousSearchValue.current = searchQuery;
      return;
    }
    if (previousSearchValue.current === searchQuery) {
      return;
    }
    previousSearchValue.current = searchQuery;
    const timeoutId = setTimeout(() => {
      const currentParams = new URLSearchParams(window.location.search);
      if (searchQuery) {
        currentParams.set("query", searchQuery);
      } else {
        currentParams.delete("query");
      }
      currentParams.set("page", "1");
      router.push(`${pathname}?${currentParams.toString()}`, {
        scroll: false,
      });
      router.refresh();
    }, 500);
    return () => clearTimeout(timeoutId);
  }, [searchQuery, pathname, router]);

  return (
    <div className="p-6 space-y-6">
      <UrlManagementHeader
        handleBulkDelete={handleBulkDelete}
        rowSelection={rowSelection}
      />

      <UrlStatCards
        totalUrls={stats?.total_urls || 0}
        activeUrls={stats?.active_urls || 0}
        flaggedUrls={stats?.flagged_urls || 0}
        inactiveUrls={stats?.inactive_urls || 0}
      />

      <div className="bg-surface rounded-xl p-4 flex items-center gap-4 flex-wrap">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-text-muted" />
          <Input
            placeholder="Search URLs or names..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select
          value={searchParam.get("url_status") || "ALL"}
          onValueChange={handleStatusChange}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Statuses</SelectItem>
            <SelectItem value="ACTIVE">Active</SelectItem>
            <SelectItem value="EXPIRED">Expired</SelectItem>
            <SelectItem value="FLAGGED">Flagged</SelectItem>
            <SelectItem value="DISABLED">Disabled</SelectItem>
            <SelectItem value="BROKEN">Broken</SelectItem>
          </SelectContent>
        </Select>
        <Select
          value={searchParam.get("date_order") || "DEFAULT"}
          onValueChange={handleDateOrderChange}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Date Order" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="DEFAULT">Default Order</SelectItem>
            <SelectItem value="-created_at">Newest First</SelectItem>
            <SelectItem value="created_at">Oldest First</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <AdminUrlDataTable
        columns={adminUrlColumns}
        data={urls}
        pagination={pagination}
        control={true}
        onPageChange={handlePageChange}
        rowSelection={rowSelection}
        onRowSelectionChange={setRowSelection}
      />

      <DeleteUrlDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onConfirm={confirmBulkDelete}
        urlCount={Object.keys(rowSelection).length}
        isLoading={isDeleting}
      />
    </div>
  );
}
