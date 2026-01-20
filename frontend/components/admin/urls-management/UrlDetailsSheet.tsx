"use client";

import { UrlResponse } from "@/api-types";
import {
    Sheet,
    SheetContent,
    SheetDescription,
    SheetHeader,
    SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { 
    ExternalLink, 
    Copy, 
    Calendar, 
    MousePointerClick, 
    Clock, 
    ShieldCheck,
    Globe
} from "lucide-react";
import { toast } from "sonner";

interface UrlDetailsSheetProps {
    url: UrlResponse | null;
    isOpen: boolean;
    onClose: () => void;
}

export default function UrlDetailsSheet({ url, isOpen, onClose }: UrlDetailsSheetProps) {
    if (!url) return null;

    const copyToClipboard = (text: string) => {
        navigator.clipboard.writeText(text);
        toast.success("Copied to clipboard");
    };

    const getStatusVariant = (state: string) => {
        switch (state.toLowerCase()) {
            case "active":
                return "success";
            case "expired":
                return "destructive";
            case "flagged":
                return "destructive";
            default:
                return "secondary";
        }
    };

    return (
        <Sheet open={isOpen} onOpenChange={onClose}>
            <SheetContent className="bg-surface border-border-subtle text-text-main sm:max-w-md overflow-y-auto">
                <SheetHeader className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                        <Badge variant={getStatusVariant(url.url_status.state)}>
                            {url.url_status.state}
                        </Badge>
                        <span className="text-xs text-text-muted flex items-center gap-1">
                            <Clock className="h-3 w-3" />
                            ID: {url.id}
                        </span>
                    </div>
                    <SheetTitle className="text-2xl font-bold text-text-main">
                        {url.name || "Untitled URL"}
                    </SheetTitle>
                    <SheetDescription className="text-text-muted">
                        Detailed overview and analytics for this shortened link.
                    </SheetDescription>
                </SheetHeader>

                <div className="space-y-8">
                    {/* Link Info Section */}
                    <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-text-muted uppercase tracking-wider">Link Details</h4>
                        <div className="bg-background/50 rounded-xl p-4 border border-border-subtle space-y-4">
                            <div>
                                <p className="text-xs text-text-muted mb-1">Short URL</p>
                                <div className="flex items-center justify-between gap-2">
                                    <span className="text-brand-blue font-mono font-medium truncate">
                                        {url.short_url}
                                    </span>
                                    <Button 
                                        variant="ghost" 
                                        size="icon-sm" 
                                        onClick={() => copyToClipboard(`${window.location.origin}/${url.short_url}`)}
                                    >
                                        <Copy className="h-4 w-4" />
                                    </Button>
                                </div>
                            </div>
                            <div>
                                <p className="text-xs text-text-muted mb-1">Destination URL</p>
                                <div className="flex items-center justify-between gap-2">
                                    <span className="text-sm text-text-main truncate max-w-[280px]">
                                        {url.long_url}
                                    </span>
                                    <a 
                                        href={url.long_url} 
                                        target="_blank" 
                                        rel="noopener noreferrer"
                                        className="p-2 hover:bg-accent rounded-md transition-colors"
                                    >
                                        <ExternalLink className="h-4 w-4 text-text-muted hover:text-brand-blue" />
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-background/50 rounded-xl p-4 border border-border-subtle">
                            <div className="flex items-center gap-2 mb-1">
                                <MousePointerClick className="h-4 w-4 text-brand-blue" />
                                <p className="text-xs text-text-muted">Total Clicks</p>
                            </div>
                            <p className="text-xl font-bold text-text-main">{url.visits.toLocaleString()}</p>
                        </div>
                        <div className="bg-background/50 rounded-xl p-4 border border-border-subtle">
                            <div className="flex items-center gap-2 mb-1">
                                <Calendar className="h-4 w-4 text-brand-blue" />
                                <p className="text-xs text-text-muted">Created On</p>
                            </div>
                            <p className="text-sm font-bold text-text-main">
                                {new Date(url.created_at).toLocaleDateString()}
                            </p>
                        </div>
                    </div>

                    {/* Metadata Section */}
                    <div className="space-y-4">
                        <h4 className="text-sm font-semibold text-text-muted uppercase tracking-wider">Metadata</h4>
                        <div className="space-y-3">
                            <div className="flex items-center justify-between py-2 border-b border-border-subtle">
                                <div className="flex items-center gap-2">
                                    <ShieldCheck className="h-4 w-4 text-text-muted" />
                                    <span className="text-sm text-text-main">Custom Alias</span>
                                </div>
                                <span className="text-sm text-text-muted">{url.is_custom_alias ? "Yes" : "No"}</span>
                            </div>
                            <div className="flex items-center justify-between py-2 border-b border-border-subtle">
                                <div className="flex items-center gap-2">
                                    <Globe className="h-4 w-4 text-text-muted" />
                                    <span className="text-sm text-text-main">Last Accessed</span>
                                </div>
                                <span className="text-sm text-text-muted">
                                    {url.last_accessed ? new Date(url.last_accessed).toLocaleDateString() : "Never"}
                                </span>
                            </div>
                            <div className="flex items-center justify-between py-2">
                                <div className="flex items-center gap-2">
                                    <Clock className="h-4 w-4 text-text-muted" />
                                    <span className="text-sm text-text-main">Expiry Date</span>
                                </div>
                                <span className="text-sm text-text-muted">
                                    {url.expiry_date ? new Date(url.expiry_date).toLocaleDateString() : "Never"}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Action Buttons */}
                    <div className="pt-6 flex gap-3">
                        <Button className="flex-1 bg-brand-blue hover:bg-brand-blue/90 text-white">
                            Edit URL
                        </Button>
                        <Button variant="destructive" className="flex-1">
                            Delete URL
                        </Button>
                    </div>
                </div>
            </SheetContent>
        </Sheet>
    );
}
