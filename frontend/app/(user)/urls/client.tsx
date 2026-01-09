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
                        className="pl-10 pr-4 py-2 w-1/2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent"
                    />
                </div>
                <Select>
                    <SelectTrigger className="w-45 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent">
                        <SelectValue placeholder="Status: All" />
                    </SelectTrigger>
                    <SelectContent className="border border-input bg-popover text-popover-foreground">
                        <SelectItem value="all">Status: All</SelectItem>
                        <SelectItem value="active">Active</SelectItem>
                        <SelectItem value="archived">Archived</SelectItem>
                    </SelectContent>
                </Select>
                <Select>
                    <SelectTrigger className="w-45 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent">
                        <SelectValue placeholder="Date Created" />
                    </SelectTrigger>
                    <SelectContent className="border border-input bg-popover text-popover-foreground">
                        <SelectItem value="date-created">
                            Date Created
                        </SelectItem>
                        <SelectItem value="newest-first">
                            Newest First
                        </SelectItem>
                        <SelectItem value="oldest-first">
                            Oldest First
                        </SelectItem>
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
