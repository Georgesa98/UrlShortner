"use client";

import { Button } from "@/components/ui/button";
import { Plus, Trash2 } from "lucide-react";
import UrlDialog from "@/components/tables/url/UrlDialog";
import { RowSelectionState } from "@tanstack/react-table";

export default function UrlManagementHeader({
  handleBulkDelete,
  rowSelection,
}: {
  handleBulkDelete: () => void;
  rowSelection: RowSelectionState;
}) {
  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 className="text-2xl font-bold text-text-main">URL Management</h1>
        <p className="text-sm text-text-muted">
          Manage and monitor all shortened URLs on the platform
        </p>
      </div>
      <div className="flex items-center gap-3 w-full sm:w-auto">
        <UrlDialog
          mode="create"
          trigger={
            <Button className="gap-2">
              <Plus className="h-4 w-4" />
              <span>New URL</span>
            </Button>
          }
        />
        {Object.keys(rowSelection).length > 0 && (
          <Button
            variant="destructive"
            onClick={handleBulkDelete}
            className="gap-2 ml-4"
          >
            <Trash2 className="h-4 w-4" />
            Bulk Delete ({Object.keys(rowSelection).length})
          </Button>
        )}
      </div>
    </div>
  );
}
