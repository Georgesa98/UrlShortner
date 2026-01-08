"use client";
import { ListUrlsResponse } from "@/api-types";
import { columns } from "@/components/tables/url/columns";
import { UrlDataTable } from "@/components/tables/url/data-table";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export default function MyUrls({ data }: { data: ListUrlsResponse }) {
    const router = useRouter();
    const pathname = usePathname();
    const searchParam = useSearchParams();
    function handlePageChange(newPage: number) {
        const params = new URLSearchParams(searchParam.toString());
        params.set("page", newPage.toString());
        router.push(`${pathname}?${params.toString()}`, { scroll: false });
        router.refresh();
    }
    return (
        <div className="flex flex-col gap-8">
            <div className="flex justify-between">
                <div>
                    <h1 className="font-black text-2xl">My Urls</h1>
                    <p className="text-muted-foreground text-sm">
                        Manage, track, and edit your shortened links
                    </p>
                </div>
                <Button className="place-self-end">
                    <Plus />
                    Create New
                </Button>
            </div>
            <UrlDataTable
                control={true}
                columns={columns}
                data={data.urls}
                pagination={data.pagination}
                onPageChange={handlePageChange}
            />
        </div>
    );
}
