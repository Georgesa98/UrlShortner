"use client";

import { useEffect, useRef, useState } from "react";
import { UrlResponse, Pagination } from "@/api-types";
import UrlStatCards from "@/components/admin/urls-management/UrlStatCards";
import UrlManagementHeader from "@/components/admin/urls-management/UrlManagementHeader";
import UrlDetailsSheet from "@/components/admin/urls-management/UrlDetailsSheet";
import { AdminUrlDataTable } from "@/components/tables/admin-url/data-table";
import { adminUrlColumns } from "@/components/tables/admin-url/columns";
import { toast } from "sonner";
import { useRouter, usePathname, useSearchParams } from "next/navigation";

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
    const router = useRouter();
    const pathname = usePathname();
    const searchParam = useSearchParams();
    const handleAddUrl = () => {
        toast.info("Create URL dialog would open here");
    };
    const [searchQuery, setSearchQuery] = useState(
        searchParam.get("query") || ""
    );
    const isInitialMount = useRef(true);
    const previousSearchValue = useRef(searchQuery);
    const [selectedUrl, setSelectedUrl] = useState<UrlResponse | null>(null);

    const handleRowClick = (url: UrlResponse) => {
        setSelectedUrl(url);
        setIsSheetOpen(true);
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
                onPageChange={handlePageChange}
            />

            <UrlDetailsSheet
                url={selectedUrl}
                isOpen={isSheetOpen}
                onClose={() => setIsSheetOpen(false)}
            />
        </div>
    );
}
