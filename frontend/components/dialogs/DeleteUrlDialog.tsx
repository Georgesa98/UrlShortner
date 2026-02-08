"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";

interface DeleteUrlDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: () => void;
  urlCount: number;
  isLoading?: boolean;
}

export function DeleteUrlDialog({
  open,
  onOpenChange,
  onConfirm,
  urlCount,
  isLoading = false,
}: DeleteUrlDialogProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-destructive/10">
              <AlertTriangle className="h-5 w-5 text-destructive" />
            </div>
            <DialogTitle>Delete URL{urlCount > 1 ? "s" : ""}?</DialogTitle>
          </div>
          <DialogDescription className="pt-3">
            Are you sure you want to delete {urlCount} URL
            {urlCount > 1 ? "s" : ""}? This action cannot be undone and will
            permanently remove {urlCount > 1 ? "these URLs" : "this URL"} from
            the system.
          </DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button
            type="button"
            variant="outline"
            onClick={(e) => {
              e.stopPropagation();
              onOpenChange(false);
            }}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={(e) => {
              e.stopPropagation();
              onConfirm();
            }}
            disabled={isLoading}
          >
            {isLoading ? "Deleting..." : "Delete"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
