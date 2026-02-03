import { Button } from "@/components/ui/button";
import { Zap } from "lucide-react";

interface CreateUrlDialogFooterProps {
  batchMode: boolean;
  onCancel: () => void;
  onSubmit: () => void;
  isSubmitting?: boolean;
}

export function CreateUrlDialogFooter({
  batchMode,
  onCancel,
  onSubmit,
  isSubmitting = false,
}: CreateUrlDialogFooterProps) {
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
        Create Link
        <Zap size={16} className="ml-1" />
      </Button>
    </div>
  );
}
