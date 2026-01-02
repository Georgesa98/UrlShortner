import { toast } from "sonner";

export async function copyToClipboard(text: string) {
    try {
        await navigator.clipboard.writeText(text);
        toast.success("short link has been copied");
    } catch (err) {
        console.error("failed to copy text", err);
        toast.error("failed to copy text.");
    }
}
