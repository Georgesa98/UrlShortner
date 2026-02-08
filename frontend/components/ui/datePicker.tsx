"use client";

import * as React from "react";
import { ChevronDownIcon, X } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";

interface DatePickerProps {
    value?: Date;
    onChange?: (date: Date | undefined) => void;
    onBlur?: () => void;
    id?: string;
    name?: string;
    "aria-invalid"?: boolean;
}

export function DatePicker({
    value,
    onChange,
    onBlur,
    id,
    name,
    "aria-invalid": ariaInvalid,
    ...props
}: DatePickerProps) {
    const [open, setOpen] = React.useState(false);

    const handleSelect = (date: Date | undefined) => {
        onChange?.(date);
        setOpen(false);
    };

    const handleClear = (e: React.MouseEvent) => {
        e.stopPropagation();
        onChange?.(undefined);
    };

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    id={id}
                    name={name}
                    aria-invalid={ariaInvalid}
                    className="w-full justify-between font-normal"
                    onBlur={onBlur}
                    {...props}
                >
                    <span className={value ? "" : "text-muted-foreground"}>
                        {value ? value.toLocaleDateString() : "Select date (optional)"}
                    </span>
                    <div className="flex items-center gap-1">
                        {value && (
                            <X
                                className="h-4 w-4 opacity-50 hover:opacity-100 transition-opacity"
                                onClick={handleClear}
                            />
                        )}
                        <ChevronDownIcon className="h-4 w-4" />
                    </div>
                </Button>
            </PopoverTrigger>
            <PopoverContent
                className="w-auto overflow-hidden p-0"
                align="start"
            >
                <Calendar
                    mode="single"
                    selected={value}
                    captionLayout="dropdown"
                    onSelect={handleSelect}
                />
            </PopoverContent>
        </Popover>
    );
}
