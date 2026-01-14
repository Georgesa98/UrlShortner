"use client";

import { UrlResponse } from "@/api-types";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { IOGResult } from "@devmehq/open-graph-extractor";
import { CheckCircle, ArrowRight, X, ExternalLink } from "lucide-react";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function RedirectPage({
    data,
    urlMetaData,
}: {
    data: UrlResponse | undefined;
    urlMetaData: IOGResult | undefined;
}) {
    const [countdown, setCountdown] = useState(5);
    const [isCancelled, setIsCancelled] = useState(false);
    const router = useRouter();

    useEffect(() => {
        if (isCancelled || !data?.long_url) return;

        if (countdown === 0) {
            router.push(data.long_url);
            return;
        }

        const timer = setTimeout(() => {
            setCountdown((prev) => prev - 1);
        }, 1000);

        return () => clearTimeout(timer);
    }, [countdown, isCancelled, data?.long_url]);

    const metaData = urlMetaData as any;
    const domain = data?.long_url ? new URL(data.long_url).hostname : "";
    const title = String(
        metaData?.ogTitle || metaData?.title || "No title found"
    );
    const ogImage = String(
        metaData?.ogImage?.[0]?.url ||
            metaData?.ogImage?.url ||
            (typeof metaData?.ogImage === "string" ? metaData.ogImage : "") ||
            ""
    );

    const handleGoNow = () => {
        if (data?.long_url) {
            router.push(data.long_url);
        }
    };

    const handleCancel = () => {
        setIsCancelled(true);
    };

    return (
        <section className="min-h-screen w-full flex flex-col items-center justify-center text-white p-4">
            <div className="flex flex-col items-center gap-6 w-full max-w-lg text-center">
                {/* Header Section */}
                <div className="flex flex-col items-center gap-4">
                    <Badge
                        variant="success"
                        className="bg-green-500/10 text-green-500 border-green-500/20 px-4 py-1.5 text-xs font-bold tracking-wider uppercase"
                    >
                        <CheckCircle className="size-4 mr-2" /> VERIFIED SAFE
                        LINK
                    </Badge>
                    <h1 className="text-3xl md:text-3xl font-bold tracking-tight">
                        You are being redirected
                    </h1>
                    <p className="text-gray-400 text-sm md:text-sm max-w-md">
                        We are taking you to your destination shortly.
                    </p>
                </div>

                {/* Preview Card */}
                <Card className="w-full bg-[#131920] border-[#1E252E] overflow-hidden rounded-2xl shadow-2xl relative">
                    <div className="absolute inset-0 bg-gradient-to-b from-blue-500/5 to-transparent pointer-events-none" />
                    <CardContent className="p-0">
                        {/* Image Preview Area */}
                        <div className="relative aspect-video w-full bg-[#1A2129] flex items-center justify-center overflow-hidden">
                            {ogImage ? (
                                <img
                                    src={ogImage}
                                    alt={title}
                                    className="w-full h-full object-cover opacity-60"
                                />
                            ) : (
                                <div className="absolute inset-0 bg-gradient-to-br from-[#1A2129] to-[#0B1015]" />
                            )}

                            {/* Overlay Info */}
                            <div className="absolute inset-0 p-8 flex flex-col justify-end text-left bg-gradient-to-t from-[#131920] via-[#131920]/40 to-transparent">
                                <div className="flex items-center gap-3 mb-6">
                                    <div className="size-10 rounded-xl bg-[#1E252E] border border-[#2D3643] flex items-center justify-center overflow-hidden shrink-0">
                                        {ogImage ? (
                                            <img
                                                src={ogImage}
                                                className="size-full object-cover"
                                            />
                                        ) : (
                                            <ExternalLink className="size-5 text-gray-400" />
                                        )}
                                    </div>
                                    <span className="text-gray-400 font-medium bg-[#1E252E]/50 px-3 py-1 rounded-lg text-sm border border-[#2D3643]/50">
                                        {domain}
                                    </span>
                                </div>
                                <h3 className="text-2xl font-bold mb-2 line-clamp-2 leading-tight">
                                    {title}
                                </h3>
                                <p className="text-gray-500 text-sm font-medium truncate max-w-md">
                                    {String(data?.long_url || "")}
                                </p>
                            </div>
                        </div>

                        {/* Progress Section */}
                        <div className="p-8 pt-6">
                            <div className="flex justify-between items-center mb-4">
                                <span className="text-blue-400 font-semibold flex items-center gap-2">
                                    {isCancelled
                                        ? "Redirect cancelled"
                                        : "Redirecting automatically"}
                                </span>
                                {!isCancelled && (
                                    <span className="text-xl font-bold text-white">
                                        {countdown}s
                                    </span>
                                )}
                            </div>
                            {!isCancelled && (
                                <Progress
                                    value={((5 - countdown) / 5) * 100}
                                    className="h-2 bg-[#1E252E]"
                                />
                            )}
                        </div>
                    </CardContent>
                </Card>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md">
                    <Button
                        size="lg"
                        className="flex-1  hover:bg-blue-500 text-white rounded-xl h-14 text-lg font-bold"
                        onClick={handleGoNow}
                    >
                        Go Now <ArrowRight className="ml-2 size-5" />
                    </Button>
                    <Button
                        size="lg"
                        variant="outline"
                        className="flex-1 border-[#1E252E] bg-transparent hover:bg-[#1E252E] text-white rounded-xl h-14 text-lg font-bold"
                        onClick={handleCancel}
                    >
                        <X className="mr-2 size-5" /> Cancel Redirect
                    </Button>
                </div>

                {/* Footer */}
                <p className="text-gray-500 text-sm max-w-sm leading-relaxed">
                    This link was scanned by ShortURL Shield™ and no threats
                    were found. If you believe this link is malicious, please{" "}
                    <Link
                        href="/report"
                        className="text-blue-400 hover:underline"
                    >
                        report it here
                    </Link>
                    .
                </p>
            </div>
        </section>
    );
}
