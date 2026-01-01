"use client";
import { ColumnDef } from "@tanstack/react-table";
import { BarChart, Copy, Edit2, QrCode } from "lucide-react";
export type Url = {
    id: string;
    name: string;
    short_url: string;
    long_url: string;
    status: "ACTIVE" | "EXPIRED" | "FLAGGED" | "DISABLED" | "BROKEN";
    created_at: string;
    clicks: number;
};

export const columns: ColumnDef<Url>[] = [
    {
        accessorKey: "linkInformation",
        header: "LINK INFORMATION",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="flex flex-col">
                    <div className="flex items-center gap-2">
                        <span className="font-bold">{data.name}</span>
                        {data.status === "ACTIVE" && (
                            <span className="rounded-lg bg-green-500/10 px-1.5 py-0.5 text-[10px] font-bold text-green-500">
                                ACTIVE
                            </span>
                        )}
                    </div>
                    <span className="text-sm text-blue-400">
                        {data.short_url}
                    </span>
                    <span className="max-w-75 truncate text-xs text-muted-foreground">
                        {data.long_url}
                    </span>
                </div>
            );
        },
    },
    {
        accessorKey: "created_at",
        header: "CREATED AT",
        cell: ({ row }) => (
            <span className="text-muted-foreground">
                {row.getValue("created_at")}
            </span>
        ),
    },
    {
        accessorKey: "clicks",
        header: "CLICKS",
        cell: ({ row }) => (
            <div className="flex items-center gap-2">
                <BarChart size={14} className="text-muted-foreground" />
                <span className="text-muted-foreground">
                    {row.getValue("clicks")}
                </span>
            </div>
        ),
    },
    {
        id: "actions",
        header: "ACTIONS",
        cell: () => {
            return (
                <div className="flex items-center gap-4 text-muted-foreground">
                    <button className="hover:text-white transition-colors">
                        <Copy size={18} />
                    </button>
                    <button className="hover:text-white transition-colors">
                        <Edit2 size={18} />
                    </button>
                    <button className="hover:text-white transition-colors">
                        <QrCode size={18} />
                    </button>
                </div>
            );
        },
    },
];
