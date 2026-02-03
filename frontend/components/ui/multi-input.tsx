"use client";

import * as React from "react";
import { X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import {
    Command,
    CommandEmpty,
    CommandGroup,
    CommandInput,
    CommandItem,
    CommandList,
} from "@/components/ui/command";
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";

export interface MultiInputOption {
    value: string;
    label: string;
    icon?: string;
}

interface MultiInputProps {
    options: MultiInputOption[];
    selected: string[];
    onChange: (selected: string[]) => void;
    placeholder?: string;
    emptyText?: string;
    className?: string;
}

export function MultiInput({
    options,
    selected,
    onChange,
    placeholder = "Select items...",
    emptyText = "No items found.",
    className,
}: MultiInputProps) {
    const [open, setOpen] = React.useState(false);
    const [search, setSearch] = React.useState("");

    const handleSelect = (value: string) => {
        if (selected.includes(value)) {
            onChange(selected.filter((item) => item !== value));
        } else {
            onChange([...selected, value]);
        }
        setSearch("");
    };

    const handleRemove = (value: string) => {
        onChange(selected.filter((item) => item !== value));
    };

    const selectedOptions = options.filter((option) =>
        selected.includes(option.value)
    );

    return (
        <Popover open={open} onOpenChange={setOpen}>
            <PopoverTrigger asChild>
                <div
                    className={cn(
                        "flex min-h-12 w-full flex-wrap gap-2 rounded-md border border-input bg-surface px-3 py-2 text-sm cursor-pointer hover:bg-surface-hover transition-colors",
                        className
                    )}
                >
                    {selectedOptions.length > 0 ? (
                        selectedOptions.map((option) => (
                            <Badge
                                key={option.value}
                                variant="secondary"
                                className="gap-1 pr-1"
                            >
                                {option.icon && (
                                    <span className="mr-1">{option.icon}</span>
                                )}
                                {option.label}
                                <button
                                    type="button"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        handleRemove(option.value);
                                    }}
                                    className="ml-1 rounded-full hover:bg-muted p-0.5"
                                >
                                    <X className="h-3 w-3" />
                                </button>
                            </Badge>
                        ))
                    ) : (
                        <span className="text-muted-foreground">
                            {placeholder}
                        </span>
                    )}
                </div>
            </PopoverTrigger>
            <PopoverContent className="w-full p-0" align="start">
                <Command>
                    <CommandInput
                        placeholder={placeholder}
                        value={search}
                        onValueChange={setSearch}
                    />
                    <CommandList>
                        <CommandEmpty>{emptyText}</CommandEmpty>
                        <CommandGroup>
                            {options
                                .filter(
                                    (option) =>
                                        option.label
                                            .toLowerCase()
                                            .includes(search.toLowerCase()) ||
                                        option.value
                                            .toLowerCase()
                                            .includes(search.toLowerCase())
                                )
                                .map((option) => (
                                    <CommandItem
                                        key={option.value}
                                        value={option.value}
                                        onSelect={() => handleSelect(option.value)}
                                        className="cursor-pointer"
                                    >
                                        <div
                                            className={cn(
                                                "mr-2 flex h-4 w-4 items-center justify-center rounded-sm border border-primary",
                                                selected.includes(option.value)
                                                    ? "bg-primary text-primary-foreground"
                                                    : "opacity-50"
                                            )}
                                        >
                                            {selected.includes(option.value) && (
                                                <span className="text-xs">✓</span>
                                            )}
                                        </div>
                                        {option.icon && (
                                            <span className="mr-2">{option.icon}</span>
                                        )}
                                        {option.label}
                                    </CommandItem>
                                ))}
                        </CommandGroup>
                    </CommandList>
                </Command>
            </PopoverContent>
        </Popover>
    );
}
