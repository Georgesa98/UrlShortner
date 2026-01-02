"use client";
import { UrlResponse } from "@/api-types";
import { columns } from "@/components/tables/url/columns";
import { UrlDataTable } from "@/components/tables/url/data-table";
import { myUrlsDummyData } from "@/components/tables/url/dummy-data";
import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function MyUrls({ data }: { data: UrlResponse[] | undefined }) {
    console.log(data);

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
            <UrlDataTable columns={columns} data={myUrlsDummyData} />
        </div>
    );
}
