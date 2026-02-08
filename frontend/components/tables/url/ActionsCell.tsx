"use client";
import { UrlResponse } from "@/api-types";
import { copyToClipboard } from "@/lib/clipboard";
import { Copy, Edit2, Trash2 } from "lucide-react";
import QrCodeDialog from "./QrCodeDialog";
import UrlDialog from "./UrlDialog";
import { DeleteUrlDialog } from "@/components/dialogs/DeleteUrlDialog";
import { deleteUrlAction } from "@/app/(user)/urls/server";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useState } from "react";

interface ActionsCellProps {
  data: UrlResponse;
}

export function ActionsCell({ data }: ActionsCellProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const router = useRouter();

  const handleDeleteSingleUrl = async () => {
    setIsDeleting(true);
    try {
      const response = await deleteUrlAction(data.short_url);
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
    <div className="flex items-center gap-4 text-muted-foreground">
      <button
        className="hover:text-white transition-colors"
        onClick={(e) => {
          copyToClipboard(data.short_url);
          e.stopPropagation();
        }}
      >
        <Copy size={18} />
      </button>
      <div onClick={(e) => e.stopPropagation()}>
        <UrlDialog
          mode="update"
          urlData={data}
          open={isEditDialogOpen}
          onOpenChange={setIsEditDialogOpen}
          trigger={
            <button
              className="hover:text-white transition-colors"
              onClick={() => setIsEditDialogOpen(true)}
            >
              <Edit2 size={18} />
            </button>
          }
        />
      </div>
      <button
        className="hover:text-destructive transition-colors"
        onClick={(e) => {
          e.stopPropagation();
          setIsDeleteDialogOpen(true);
        }}
      >
        <Trash2 size={18} />
      </button>
      <div onClick={(e) => e.stopPropagation()}>
        <QrCodeDialog shortUrl={data.short_url} />
      </div>

      <div onClick={(e) => e.stopPropagation()}>
        <DeleteUrlDialog
          open={isDeleteDialogOpen}
          onOpenChange={setIsDeleteDialogOpen}
          onConfirm={handleDeleteSingleUrl}
          urlCount={1}
          isLoading={isDeleting}
        />
      </div>
    </div>
  );
}
