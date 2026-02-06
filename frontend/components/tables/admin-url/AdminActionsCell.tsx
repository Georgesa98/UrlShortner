"use client";
import { UrlResponse } from "@/api-types";
import { Button } from "@/components/ui/button";
import { Copy, Edit2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import UrlDialog from "@/components/tables/url/UrlDialog";
import { DeleteUrlDialog } from "@/components/dialogs/DeleteUrlDialog";
import { bulkDeleteUrlsAction } from "@/app/admin/urls-management/server";
import { useRouter } from "next/navigation";
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
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();

  const handleDeleteSingleUrl = async () => {
    setIsDeleting(true);
    try {
      const response = await bulkDeleteUrlsAction({ url_ids: [data.id] });
      if (response.success) {
        toast.success("URL deleted successfully");
        router.refresh();
      } else {
        toast.error(response.message);
      }
    } catch (error) {
      toast.error("Failed to delete URL");
    } finally {
      setIsDeleting(false);
      setIsDeleteDialogOpen(false);
    }
  };

  return (
    <div className="flex items-center justify-end gap-2 px-6">
      <Button
        variant="ghost"
        size="icon-sm"
        onClick={(e) => {
          e.stopPropagation();
          copyToClipboard(`${window.location.origin}/${data.short_url}`);
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
          setIsDeleteDialogOpen(true);
        }}
        className="text-text-muted hover:text-destructive"
      >
        <Trash2 className="h-4 w-4" />
      </Button>

      <DeleteUrlDialog
        open={isDeleteDialogOpen}
        onOpenChange={setIsDeleteDialogOpen}
        onConfirm={handleDeleteSingleUrl}
        urlCount={1}
        isLoading={isDeleting}
      />
    </div>
  );
}
