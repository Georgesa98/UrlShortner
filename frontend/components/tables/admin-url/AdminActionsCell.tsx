"use client";
import { UrlResponse } from "@/api-types";
import { Button } from "@/components/ui/button";
import { Copy, Edit2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import UrlDialog from "@/components/tables/url/UrlDialog";
import { useState } from "react";

const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
};

interface AdminActionsCellProps {
    data: UrlResponse;
}

export function AdminActionsCell({ data }: AdminActionsCellProps) {
    const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

    return (
        <div className="flex items-center justify-end gap-2 px-6">
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
            <div onClick={(e) => e.stopPropagation()}>
                <UrlDialog
                    mode="update"
                    urlData={data}
                    open={isEditDialogOpen}
                    onOpenChange={setIsEditDialogOpen}
                    trigger={
                        <Button
                            variant="ghost"
                            size="icon-sm"
                            onClick={() => setIsEditDialogOpen(true)}
                            className="text-text-muted hover:text-brand-blue"
                        >
                            <Edit2 className="h-4 w-4" />
                        </Button>
                    }
                />
            </div>
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
}
