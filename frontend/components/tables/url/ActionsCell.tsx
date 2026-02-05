"use client";
import { UrlResponse } from "@/api-types";
import { copyToClipboard } from "@/lib/clipboard";
import { Copy, Edit2 } from "lucide-react";
import QrCodeDialog from "./QrCodeDialog";
import UrlDialog from "./UrlDialog";
import { useState } from "react";

interface ActionsCellProps {
  data: UrlResponse;
}

export function ActionsCell({ data }: ActionsCellProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);

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
      <div onClick={(e) => e.stopPropagation()}>
        <QrCodeDialog shortUrl={data.short_url} />
      </div>
    </div>
  );
}
