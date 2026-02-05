import { Button } from "@/components/ui/button";
import { Zap } from "lucide-react";

interface UrlDialogFooterProps {
  mode: "create" | "update";
  batchMode: boolean;
  onCancel: () => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
}

export function UrlDialogFooter({
  mode,
  batchMode,
  onCancel,
  onSubmit,
  isSubmitting = false,
}: UrlDialogFooterProps) {
  const buttonText = mode === "update" ? "Update Link" : "Create Link";
  
  return (
    <div className="place-self-end flex items-center gap-2 shrink-0 pt-4">
      <Button
        size="lg"
        variant="ghost"
        onClick={onCancel}
        disabled={isSubmitting}
      >
        Cancel
      </Button>
      <Button
        size="lg"
        className="bg-gradient-blue-purple hover:shadow-glow-blue transition-shadow"
        onClick={onSubmit}
        disabled={isSubmitting}
      >
        {buttonText}
        <Zap size={16} className="ml-1" />
      </Button>
    </div>
  );
}
