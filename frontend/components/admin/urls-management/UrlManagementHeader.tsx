"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Search, Plus, Filter } from "lucide-react";

export default function UrlManagementHeader({
    searchQuery,
    setSearchQuery,
    onAddUrl,
}: {
    searchQuery: string;
    setSearchQuery: (query: string) => void;
    onAddUrl: () => void;
}) {
    return (
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
            <div>
                <h1 className="text-2xl font-bold text-text-main">URL Management</h1>
                <p className="text-sm text-text-muted">
                    Manage and monitor all shortened URLs on the platform
                </p>
            </div>
            <div className="flex items-center gap-3 w-full sm:w-auto">
                <div className="relative flex-1 sm:flex-initial sm:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-muted" />
                    <Input
                        placeholder="Search URLs or names..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9 bg-surface border-none text-text-main"
                    />
                </div>
                <Button variant="outline" size="icon" className="text-text-muted">
                    <Filter className="h-4 w-4" />
                </Button>
                <Button onClick={onAddUrl} className="gap-2">
                    <Plus className="h-4 w-4" />
                    <span>New URL</span>
                </Button>
            </div>
        </div>
    );
}
