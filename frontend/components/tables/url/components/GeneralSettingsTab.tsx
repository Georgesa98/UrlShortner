import {
    createBatchLinkFormSchema,
    createLinkFormSchema,
} from "@/app/(user)/urls/schema";
import { Separator } from "@/components/ui/separator";
import { UseFormReturn } from "react-hook-form";
import z from "zod";
import { BatchModeToggle } from "./BatchModeToggle";
import { BatchUrlForm } from "./BatchUrlForm";
import { SingleUrlForm } from "./SingleUrlForm";

interface GeneralSettingsTabProps {
    batchMode: boolean;
    setBatchMode: (value: boolean) => void;
    singleUrlForm: UseFormReturn<z.infer<typeof createLinkFormSchema>>;
    batchUrlForm: UseFormReturn<z.infer<typeof createBatchLinkFormSchema>>;
    hostname: string;
    isUpdateMode?: boolean;
    hideBatchToggle?: boolean;
}

export function GeneralSettingsTab({
    batchMode,
    setBatchMode,
    singleUrlForm,
    batchUrlForm,
    hostname,
    isUpdateMode = false,
    hideBatchToggle = false,
}: GeneralSettingsTabProps) {
    return (
        <>
            <Separator className="w-full" />

            {!hideBatchToggle && (
                <BatchModeToggle
                    checked={batchMode}
                    onCheckedChange={setBatchMode}
                />
            )}

            {!batchMode ? (
                <SingleUrlForm 
                    control={singleUrlForm.control} 
                    hostname={hostname}
                    isUpdateMode={isUpdateMode}
                />
            ) : (
                <BatchUrlForm control={batchUrlForm.control} />
            )}
        </>
    );
}
