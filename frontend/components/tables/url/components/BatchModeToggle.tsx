import { Switch } from "@/components/ui/switch";
import { Layers } from "lucide-react";

interface BatchModeToggleProps {
    checked: boolean;
    onCheckedChange: (checked: boolean) => void;
}

export function BatchModeToggle({
    checked,
    onCheckedChange,
}: BatchModeToggleProps) {
    return (
        <div className="flex items-center justify-between p-4 rounded-lg bg-surface border border-border">
            <div className="flex items-center gap-3">
                <div className="p-2 rounded-md bg-primary/10">
                    <Layers size={20} className="text-primary" />
                </div>
                <div>
                    <h3 className="font-bold text-sm">Batch Mode</h3>
                    <p className="text-sm text-muted-foreground">
                        Shorten multiple links at once
                    </p>
                </div>
            </div>
            <Switch checked={checked} onCheckedChange={onCheckedChange} />
        </div>
    );
}
