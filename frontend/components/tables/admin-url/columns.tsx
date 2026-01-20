"use client";
import { UrlResponse } from "@/api-types";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Copy, Edit2, Trash2, ExternalLink } from "lucide-react";
import { toast } from "sonner";

const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
};

const getStatusVariant = (state: string) => {
    switch (state.toLowerCase()) {
        case "active":
            return "success";
        case "expired":
            return "destructive";
        case "flagged":
            return "destructive";
        default:
            return "secondary";
    }
};

export const adminUrlColumns: ColumnDef<UrlResponse>[] = [
    {
        accessorKey: "name",
        header: "Name",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="px-6 font-medium text-text-main">
                    {data.name || "Untitled"}
                </div>
            );
        },
    },
    {
        accessorKey: "short_url",
        header: "Short URL",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="flex items-center gap-2">
                    <span className="text-brand-blue font-mono text-sm">
                        {data.short_url}
                    </span>
                    <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                            e.stopPropagation();
                            copyToClipboard(
                                `${window.location.origin}/${data.short_url}`
                            );
                        }}
                        className="text-text-muted hover:text-text-main"
                    >
                        <Copy className="h-3 w-3" />
                    </Button>
                </div>
            );
        },
    },
    {
        accessorKey: "long_url",
        header: "Destination",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="max-w-[200px] truncate text-text-muted text-sm">
                    <div className="flex items-center gap-1">
                        <span className="truncate">{data.long_url}</span>
                        <a
                            href={data.long_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="text-text-muted hover:text-brand-blue"
                        >
                            <ExternalLink className="h-3 w-3" />
                        </a>
                    </div>
                </div>
            );
        },
    },
    {
        accessorKey: "created_at",
        header: "Created",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <span className="text-text-muted text-sm">
                    {new Date(data.created_at).toLocaleDateString()}
                </span>
            );
        },
    },
    {
        accessorKey: "visits",
        header: "Clicks",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="text-center text-text-main font-semibold">
                    {data.visits.toLocaleString()}
                </div>
            );
        },
    },
    {
        accessorKey: "url_status",
        header: "Status",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <Badge variant={getStatusVariant(data.url_status.state)}>
                    {data.url_status.state}
                </Badge>
            );
        },
    },
    {
        id: "actions",
        header: "Actions",
        cell: ({ row }) => {
            return (
                <div className="flex items-center justify-end gap-2 px-6">
                    <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                            e.stopPropagation();
                            toast.info("Edit dialog would open here");
                        }}
                        className="text-text-muted hover:text-brand-blue"
                    >
                        <Edit2 className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                            e.stopPropagation();
                            toast.info("Delete confirmation would open here");
                        }}
                        className="text-text-muted hover:text-destructive"
                    >
                        <Trash2 className="h-4 w-4" />
                    </Button>
                </div>
            );
        },
    },
];
