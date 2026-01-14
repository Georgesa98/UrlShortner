"use client";
import Link from "next/link";
import { Search, Home, Link as LinkIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function NotFound() {
    return (
        <div className="flex flex-col items-center justify-center h-screen px-4 text-center max-w-2xl mx-auto">
            <div className="space-y-6">
                {/* 404 - Link Broken */}
                <h1 className="text-4xl md:text-5xl font-bold text-text-main">
                    404 - Link Broken
                </h1>

                {/* Subtext */}
                <p className="text-text-muted text-lg max-w-lg mx-auto leading-relaxed">
                    We couldn't find the destination for this short URL. It
                    might have been deleted, expired, or never existed in the
                    first place.
                </p>
            </div>
            {/* Footer Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 mt-12 w-full justify-center">
                <Button
                    asChild
                    variant="secondary"
                    className="h-12 px-8 gap-3 bg-surface hover:bg-surface-hover text-text-main border-none font-bold min-w-[180px]"
                >
                    <Link href="/">
                        <Home className="h-5 w-5" />
                        Back to Home
                    </Link>
                </Button>
                <Button
                    asChild
                    className="h-12 px-8 gap-3 font-bold bg-brand-blue hover:bg-brand-blue/90 shadow-glow-blue min-w-[200px]"
                >
                    <Link href="/dashboard">
                        <LinkIcon className="h-5 w-5" />
                        Create a Short Link
                    </Link>
                </Button>
            </div>
        </div>
    );
}
