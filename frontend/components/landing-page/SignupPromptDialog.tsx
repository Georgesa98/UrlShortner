import Link from "next/link";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Check, Sparkles } from "lucide-react";

interface SignupPromptDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export default function SignupPromptDialog({
  open,
  onOpenChange,
}: SignupPromptDialogProps) {
  const features = [
    "Unlimited URL shortening",
    "Advanced analytics & insights",
    "Custom branded aliases",
    "Batch URL processing",
    "QR code generation",
    "Smart redirection rules",
  ];

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <div className="flex items-center gap-2 mb-2">
            <Sparkles className="text-brand-blue" size={24} />
            <DialogTitle className="text-2xl">
              Sign up to save your link!
            </DialogTitle>
          </div>
          <DialogDescription className="text-base">
            Create a free account to shorten URLs and unlock powerful features.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div className="space-y-2">
            {features.map((feature, index) => (
              <div key={index} className="flex items-center gap-2">
                <div className="bg-brand-blue/10 p-1 rounded-full">
                  <Check className="text-brand-blue" size={14} />
                </div>
                <span className="text-sm">{feature}</span>
              </div>
            ))}
          </div>

          <div className="flex flex-col gap-2 pt-2">
            <Link href="/signup?utm_source=landing&utm_medium=demo_form" className="w-full">
              <Button className="w-full" size="lg">
                Create Free Account
              </Button>
            </Link>
            <Link href="/login" className="w-full">
              <Button variant="outline" className="w-full" size="lg">
                Already have an account? Login
              </Button>
            </Link>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
