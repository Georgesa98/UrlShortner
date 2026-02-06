"use client";

import { useEffect, useRef, useState } from "react";
import { UrlResponse, Pagination } from "@/api-types";
import UrlStatCards from "@/components/admin/urls-management/UrlStatCards";
import UrlManagementHeader from "@/components/admin/urls-management/UrlManagementHeader";
import UrlDetailsSheet from "@/components/admin/urls-management/UrlDetailsSheet";
import { AdminUrlDataTable } from "@/components/tables/admin-url/data-table";
import { adminUrlColumns } from "@/components/tables/admin-url/columns";
import { useRouter, usePathname, useSearchParams } from "next/navigation";
import { RowSelectionState } from "@tanstack/react-table";
import { Button } from "@/components/ui/button";
import { Trash2 } from "lucide-react";
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
  const [isSheetOpen, setIsSheetOpen] = useState(false);
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
  const [selectedUrl, setSelectedUrl] = useState<UrlResponse | null>(null);

  const handleRowClick = (url: UrlResponse) => {
    setSelectedUrl(url);
    setIsSheetOpen(true);
  };

  const handleBulkDelete = () => {
    const selectedUrlIds = Object.keys(rowSelection).map((id) => parseInt(id));
    if (selectedUrlIds.length === 0) {
      toast.error("No URLs selected");
      return;
    }
    setIsDeleteDialogOpen(true);
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
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <UrlManagementHeader
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            handleBulkDelete={handleBulkDelete}
            rowSelection={rowSelection}
          />
        </div>
      </div>

      <UrlStatCards
        totalUrls={stats?.total_urls || 0}
        activeUrls={stats?.active_urls || 0}
        flaggedUrls={stats?.flagged_urls || 0}
        inactiveUrls={stats?.inactive_urls || 0}
      />

      <AdminUrlDataTable
        columns={adminUrlColumns}
        data={urls}
        pagination={pagination}
        onRowClick={handleRowClick}
        control={true}
        onPageChange={handlePageChange}
        rowSelection={rowSelection}
        onRowSelectionChange={setRowSelection}
      />

      <UrlDetailsSheet
        url={selectedUrl}
        isOpen={isSheetOpen}
        onClose={() => setIsSheetOpen(false)}
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
