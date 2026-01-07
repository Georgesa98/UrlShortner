"use client";
import { UrlResponse } from "@/api-types";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import useHostname from "@/hooks/useHostname";
import { copyToClipboard } from "@/lib/clipboard";
import { formatToClientDate } from "@/lib/formatToClientDate";
import { ColumnDef } from "@tanstack/react-table";
import { BarChart, Copy, Download, Edit2, QrCode } from "lucide-react";
import Image from "next/image";

const qrCodeDialog = (
    <Dialog>
        <DialogTrigger asChild>
            <button className="hover:text-white transition-colors">
                <QrCode size={18} />
            </button>
        </DialogTrigger>
        <DialogContent>
            <DialogTitle>Qr Code</DialogTitle>
            <Image
                width={300}
                height={300}
                alt="qrcode"
                className="place-self-center"
                src="https://placehold.co/1000/png"
            />
            <Button size="lg">
                Download PNG <Download />
            </Button>
        </DialogContent>
    </Dialog>
);
export const columns: ColumnDef<UrlResponse>[] = [
    {
        accessorKey: "linkInformation",
        header: "LINK INFORMATION",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="flex flex-col">
                    <div className="flex items-center gap-2">
                        <span className="font-bold">{data.name}</span>
                        {data.url_status.state === "ACTIVE" && (
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
                {formatToClientDate(row.getValue("created_at"))}
            </span>
        ),
    },
    {
        accessorKey: "visits",
        header: "CLICKS",
        cell: ({ row }) => (
            <div className="flex items-center gap-2">
                <BarChart size={14} className="text-muted-foreground" />
                <span className="text-muted-foreground">
                    {row.getValue("visits")}
                </span>
            </div>
        ),
    },
    {
        id: "actions",
        header: "ACTIONS",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="flex items-center gap-4 text-muted-foreground">
                    <button className="hover:text-white transition-colors">
                        <Copy
                            size={18}
                            onClick={() => copyToClipboard(data.short_url)}
                        />
                    </button>
                    <button className="hover:text-white transition-colors">
                        <Edit2 size={18} />
                    </button>
                    {qrCodeDialog}
                </div>
            );
        },
    },
];
