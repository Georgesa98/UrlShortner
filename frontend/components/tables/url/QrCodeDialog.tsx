"use client";
import axiosClient from "@/app/api/axiosClient";
import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogTrigger,
    DialogTitle,
    DialogContent,
} from "@/components/ui/dialog";
import { Download, Loader2, QrCode } from "lucide-react";
import Image from "next/image";
import { useEffect, useState } from "react";

export default function QrCodeDialog({ shortUrl }: { shortUrl: string }) {
    const [qrImageUrl, setQrImageUrl] = useState<string>("");
    const [isLoading, setIsLoading] = useState(false);

    async function fetchQrCode(open: boolean) {
        if (open && !qrImageUrl) {
            setIsLoading(true);
            try {
                const response = await axiosClient.get(`/url/qr/${shortUrl}/`, {
                    responseType: "blob",
                });

                if (response.data instanceof Blob) {
                    const imageUrl = URL.createObjectURL(response.data);
                    setQrImageUrl(imageUrl);
                }
            } catch (error) {
                console.error("Failed to fetch QR code:", error);
            }
            setIsLoading(false);
        }
    }
    useEffect(() => {
        return () => {
            if (qrImageUrl) {
                URL.revokeObjectURL(qrImageUrl);
            }
        };
    }, [qrImageUrl]);

    const handleDownload = () => {
        if (qrImageUrl) {
            const link = document.createElement("a");
            link.href = qrImageUrl;
            link.download = `qr-${shortUrl}.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    };

    return (
        <Dialog onOpenChange={fetchQrCode}>
            <DialogTrigger asChild>
                <button className="hover:text-white transition-colors">
                    <QrCode size={18} />
                </button>
            </DialogTrigger>
            <DialogContent>
                <DialogTitle>QR Code</DialogTitle>
                <div className="relative flex items-center justify-center w-75 h-75 bg-muted rounded-lg mx-auto">
                    {qrImageUrl ? (
                        <Image
                            alt="QR Code"
                            src={qrImageUrl}
                            width={300}
                            height={300}
                        />
                    ) : (
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                    )}
                </div>
                <Button
                    size="lg"
                    onClick={handleDownload}
                    disabled={!qrImageUrl}
                >
                    Download PNG <Download />
                </Button>
            </DialogContent>
        </Dialog>
    );
}
