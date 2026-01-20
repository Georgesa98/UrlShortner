"use client";

import { useState } from "react";
import { UrlResponse, Pagination } from "@/api-types";
import UrlStatCards from "@/components/admin/urls-management/UrlStatCards";
import UrlManagementHeader from "@/components/admin/urls-management/UrlManagementHeader";
import UrlDetailsSheet from "@/components/admin/urls-management/UrlDetailsSheet";
import { AdminUrlDataTable } from "@/components/tables/admin-url/data-table";
import { adminUrlColumns } from "@/components/tables/admin-url/columns";
import { toast } from "sonner";

export default function UrlsManagementPage({
    urls,
    stats,
    pagination,
}: {
    urls: UrlResponse[];
    stats: Record<string, number>;
    pagination: Pagination;
}) {
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedUrl, setSelectedUrl] = useState<UrlResponse | null>(null);
    const [isSheetOpen, setIsSheetOpen] = useState(false);

    const handleAddUrl = () => {
        toast.info("Create URL dialog would open here");
    };

    const handleRowClick = (url: UrlResponse) => {
        setSelectedUrl(url);
        setIsSheetOpen(true);
    };

    return (
        <div className="p-6 space-y-6">
            <UrlManagementHeader
                searchQuery={searchQuery}
                setSearchQuery={setSearchQuery}
                onAddUrl={handleAddUrl}
            />

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
            />

            <UrlDetailsSheet
                url={selectedUrl}
                isOpen={isSheetOpen}
                onClose={() => setIsSheetOpen(false)}
            />
        </div>
    );
}
