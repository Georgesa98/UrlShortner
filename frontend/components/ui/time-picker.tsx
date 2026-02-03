"use client";

import * as React from "react";
import { Clock } from "lucide-react";
import { Input } from "@/components/ui/input";
import { cn } from "@/lib/utils";

interface TimePickerProps {
    value?: string;
    onChange: (value: string) => void;
    placeholder?: string;
    className?: string;
    id?: string;
}

export function TimePicker({
    value = "",
    onChange,
    placeholder = "--:--",
    className,
    id,
}: TimePickerProps) {
    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        let inputValue = e.target.value.replace(/[^\d:]/g, "");
        
        // Auto-format as user types
        if (inputValue.length === 2 && !inputValue.includes(":")) {
            inputValue = inputValue + ":";
        }
        
        // Limit to HH:MM format
        if (inputValue.length > 5) {
            inputValue = inputValue.slice(0, 5);
        }
        
        onChange(inputValue);
    };

    const handleBlur = () => {
        // Validate and format on blur
        if (value) {
            const parts = value.split(":");
            if (parts.length === 2) {
                const hours = parseInt(parts[0]) || 0;
                const minutes = parseInt(parts[1]) || 0;
                
                if (hours >= 0 && hours < 24 && minutes >= 0 && minutes < 60) {
                    const formatted = `${hours.toString().padStart(2, "0")}:${minutes.toString().padStart(2, "0")}`;
                    onChange(formatted);
                }
            }
        }
    };

    return (
        <div className="relative">
            <Input
                id={id}
                type="text"
                value={value}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder={placeholder}
                className={cn("pl-10 bg-surface", className)}
                maxLength={5}
            />
            <Clock
                size={18}
                className="absolute left-3 top-1/2 text-muted-foreground -translate-y-1/2"
            />
        </div>
    );
}
