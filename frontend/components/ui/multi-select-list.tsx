"use client";

import * as React from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { cn } from "@/lib/utils";

interface MultiSelectListProps {
    options: readonly string[];
    selected: string[];
    onChange: (selected: string[]) => void;
    className?: string;
    maxHeight?: string;
}

export function MultiSelectList({
    options,
    selected,
    onChange,
    className,
    maxHeight = "200px",
}: MultiSelectListProps) {
    const handleToggle = (value: string) => {
        if (selected.includes(value)) {
            onChange(selected.filter((item) => item !== value));
        } else {
            onChange([...selected, value]);
        }
    };

    return (
        <ScrollArea className={cn("rounded-md border border-input", className)} style={{ maxHeight }}>
            <div className="p-1">
                {options.map((option) => {
                    const isSelected = selected.includes(option);
                    return (
                        <button
                            key={option}
                            type="button"
                            onClick={() => handleToggle(option)}
                            className={cn(
                                "w-full text-left px-3 py-2 text-sm rounded-sm transition-colors",
                                "hover:bg-accent hover:text-accent-foreground",
                                isSelected && "bg-primary/10 text-primary font-medium"
                            )}
                        >
                            {option}
                        </button>
                    );
                })}
            </div>
        </ScrollArea>
    );
}
