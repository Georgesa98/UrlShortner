"use client";
import { UrlResponse } from "@/api-types";
import { ColumnDef } from "@tanstack/react-table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Ban, Eye } from "lucide-react";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";

const getFlagReasonVariant = (reason: string | null) => {
    if (!reason) return "secondary";
    
    const lowerReason = reason.toLowerCase();
    if (lowerReason.includes("burst")) return "destructive";
    if (lowerReason.includes("throttle")) return "warning";
    if (lowerReason.includes("suspicious")) return "warning";
    return "secondary";
};

const getFlagReasonDisplay = (reason: string | null) => {
    if (!reason) return "Other";
    
    const lowerReason = reason.toLowerCase();
    if (lowerReason.includes("burst")) return "Burst";
    if (lowerReason.includes("throttle")) return "Throttle";
    if (lowerReason.includes("suspicious") && lowerReason.includes("user") && lowerReason.includes("agent")) {
        return "Suspicious UA";
    }
    return "Other";
};

export const fraudDetectionColumns: ColumnDef<UrlResponse>[] = [
    {
        accessorKey: "short_url",
        header: "SHORT LINK",
        cell: ({ row }) => {
            const data = row.original;
            const createdAt = new Date(data.created_at);
            const timeAgo = formatDistanceToNow(createdAt, { addSuffix: true });
            
            return (
                <div className="px-6">
                    <div className="font-mono text-sm text-brand-blue font-medium">
                        shrt.lnk/{data.short_url}
                    </div>
                    <div className="text-xs text-text-muted mt-1">
                        Created {timeAgo}
                    </div>
                </div>
            );
        },
    },
    {
        accessorKey: "long_url",
        header: "DESTINATION",
        cell: ({ row }) => {
            const data = row.original;
            return (
                <div className="max-w-[300px] truncate text-text-muted text-sm">
                    {data.long_url}
                </div>
            );
        },
    },
    {
        accessorKey: "url_status",
        header: "FLAG REASON",
        cell: ({ row }) => {
            const data = row.original;
            const reason = data.url_status.reason;
            const displayReason = getFlagReasonDisplay(reason);
            const variant = getFlagReasonVariant(reason);
            
            return (
                <Badge variant={variant}>
                    {displayReason}
                </Badge>
            );
        },
    },
    {
        id: "actions",
        header: "ACTIONS",
        cell: ({ row }) => {
            const data = row.original;
            
            return (
                <div className="flex items-center justify-end gap-2 px-6">
                    <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                            e.stopPropagation();
                            toast.info(`Ban URL: ${data.short_url}`);
                        }}
                        className="text-text-muted hover:text-destructive"
                        title="Ban URL"
                    >
                        <Ban className="h-4 w-4" />
                    </Button>
                    <Button
                        variant="ghost"
                        size="icon-sm"
                        onClick={(e) => {
                            e.stopPropagation();
                            toast.info(`View details for: ${data.short_url}`);
                        }}
                        className="text-text-muted hover:text-brand-blue"
                        title="View Details"
                    >
                        <Eye className="h-4 w-4" />
                    </Button>
                </div>
            );
        },
    },
];
