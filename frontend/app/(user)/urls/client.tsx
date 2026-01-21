"use client";
import { ListUrlsResponse } from "@/api-types";
import { columns } from "@/components/tables/url/columns";
import CreateUrlDialog from "@/components/tables/url/CreateUrlDialog";
import { UrlDataTable } from "@/components/tables/url/data-table";
import { Input } from "@/components/ui/input";
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export default function MyUrls({ data }: { data: ListUrlsResponse }) {
    const router = useRouter();
    const pathname = usePathname();
    const searchParam = useSearchParams();
    const [searchValue, setSearchValue] = useState(
        searchParam.get("query") || ""
    );
    const isInitialMount = useRef(true);
    const previousSearchValue = useRef(searchValue);
    function handlePageChange(newPage: number) {
        const params = new URLSearchParams(searchParam.toString());
        params.set("page", newPage.toString());
        router.push(`${pathname}?${params.toString()}`, { scroll: false });
        router.refresh();
    }
    function handleStatusChange(newStatus: string) {
        const params = new URLSearchParams(searchParam.toString());
        params.set("status", newStatus);
        router.push(`${pathname}?${params.toString()}`, { scroll: false });
        router.refresh();
    }
    function handleDateOrderChange(newDateOrder: string) {
        const params = new URLSearchParams(searchParam.toString());
        params.set("date_order", newDateOrder);
        router.push(`${pathname}?${params.toString()}`, { scroll: false });
        router.refresh();
    }
    useEffect(() => {
        if (isInitialMount.current) {
            isInitialMount.current = false;
            previousSearchValue.current = searchValue;
            return;
        }
        if (previousSearchValue.current === searchValue) {
            return;
        }
        previousSearchValue.current = searchValue;
        const timeoutId = setTimeout(() => {
            const currentParams = new URLSearchParams(window.location.search);
            if (searchValue) {
                currentParams.set("query", searchValue);
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
    }, [searchValue, pathname, router]);
    return (
        <div className="flex flex-col gap-8 ">
            <div className="flex justify-between">
                <div>
                    <h1 className="font-black text-2xl">My Urls</h1>
                    <p className="text-muted-foreground text-sm">
                        Manage, track, and edit your shortened links
                    </p>
                </div>
                <CreateUrlDialog buttonClassName="place-self-end" />
            </div>
            <div className="flex gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                    <Input
                        type="text"
                        placeholder="Search by keyword or URL..."
                        value={searchValue}
                        onChange={(e) => setSearchValue(e.target.value)}
                        className="pl-10 pr-4 py-2 w-1/2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                </div>
                <Select onValueChange={handleStatusChange}>
                    <SelectTrigger className="w-45 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent">
                        <SelectValue placeholder="All" defaultValue="all" />
                    </SelectTrigger>
                    <SelectContent className="border border-input bg-popover text-popover-foreground">
                        <SelectItem value="ALL">All</SelectItem>
                        <SelectItem value="ACTIVE">Active</SelectItem>
                        <SelectItem value="EXPIRED">Expired</SelectItem>
                        <SelectItem value="FLAGGED">Flagged</SelectItem>
                        <SelectItem value="DISABLED">Disabled</SelectItem>
                        <SelectItem value="BROKEN">Broken</SelectItem>
                    </SelectContent>
                </Select>
                <Select onValueChange={handleDateOrderChange}>
                    <SelectTrigger className="w-45 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent">
                        <SelectValue
                            placeholder="Date Created"
                            defaultValue="DESC"
                        />
                    </SelectTrigger>
                    <SelectContent className="border border-input bg-popover text-popover-foreground">
                        <SelectItem value="DESC">Newest First</SelectItem>
                        <SelectItem value="ASC">Oldest First</SelectItem>
                    </SelectContent>
                </Select>
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
