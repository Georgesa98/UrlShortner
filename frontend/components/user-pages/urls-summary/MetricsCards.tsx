"use client";

import axiosClient from "@/app/api/axiosClient";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { MousePointerClick, Users, QrCode, Loader2 } from "lucide-react";
import Image from "next/image";
import { useEffect, useState } from "react";
import { GetUrlSummaryResponse } from "@/api-types";

interface MetricCardProps {
    title: string;
    value: string;
    icon: React.ReactNode;
}

const MetricCard = ({ title, value, icon }: MetricCardProps) => {
    return (
        <Card>
            <CardContent className="p-4 md:p-6">
                <div className="flex justify-between items-start">
                    <div>
                        <p className="text-sm font-medium text-muted-foreground">
                            {title}
                        </p>
                        <h3 className="text-2xl font-bold mt-1">{value}</h3>
                    </div>
                    <div className="rounded-full p-3 bg-blue-500/10 text-blue-500">
                        {icon}
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

const QRCodeCard = ({ url }: { url: string }) => {
    const [qrImageUrl, setQrImageUrl] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);
    useEffect(() => {
        async function fetchQrCode() {
            setIsLoading(true);
            try {
                const response = await axiosClient.get(`/url/qr/${url}/`, {
                    responseType: "blob",
                });

                if (response.data instanceof Blob) {
                    const imageUrl = URL.createObjectURL(response.data);
                    console.log(imageUrl);

                    setQrImageUrl(imageUrl);
                }
            } catch (error) {
                console.error("Failed to fetch QR code:", error);
            }
            setIsLoading(false);
        }
        fetchQrCode();
    }, []);
    const handleDownload = () => {
        const link = document.createElement("a");
        link.href = qrImageUrl;
        link.download = `qrcode-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    return (
        <Card>
            <CardContent>
                <div className="flex items-center gap-12 ">
                    <div className="relative flex flex-col items-center mb-4">
                        {qrImageUrl ? (
                            <Image
                                src={qrImageUrl}
                                alt="QR Code for URL"
                                width={100}
                                height={100}
                                className="border rounded"
                            />
                        ) : (
                            <Loader2 className="h-8 w-8 animate-spin text-primary" />
                        )}
                    </div>
                    <div className="flex flex-col">
                        <div className="flex items-center justify-between mb-4">
                            <p className="text-sm font-medium text-muted-foreground">
                                QR Code
                            </p>
                            <QrCode className="h-5 w-5 text-blue-500" />
                        </div>
                        <Button
                            onClick={handleDownload}
                            className=" bg-blue-500 hover:bg-blue-600 text-white rounded-md text-sm transition-colors"
                            size="lg"
                        >
                            Download
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}

interface MetricsCardsProps {
    data: GetUrlSummaryResponse;
}

export default function MetricsCards({
    data,
}: MetricsCardsProps) {
    const metrics = [
        {
            title: "Total Clicks",
            value: data.basic_info.visits.toLocaleString(),
            icon: <MousePointerClick className="h-5 w-5" />,
        },
        {
            title: "Unique Visitors",
            value: data.basic_info.unique_visits.toLocaleString(),
            icon: <Users className="h-5 w-5" />,
        },
    ];

    const url = data.basic_info.short_url;

    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
            {metrics.map((metric, index) => (
                <MetricCard
                    key={index}
                    title={metric.title}
                    value={metric.value}
                    icon={metric.icon}
                />
            ))}
            {url && <QRCodeCard url={url} />}
        </div>
    );
}
