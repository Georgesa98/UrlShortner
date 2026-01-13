"use client";

import * as React from "react";
import { ChevronDownIcon } from "lucide-react";

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

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <Button
                    variant="outline"
                    id={id}
                    name={name}
                    aria-invalid={ariaInvalid}
                    className="w-48 justify-between font-normal"
                    onBlur={onBlur}
                    {...props}
                >
                    {value ? value.toLocaleDateString() : "Select date"}
                    <ChevronDownIcon />
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
