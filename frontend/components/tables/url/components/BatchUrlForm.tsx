import { createBatchLinkFormSchema } from "@/app/(user)/urls/schema";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { Control, Controller } from "react-hook-form";
import z from "zod";

interface BatchUrlFormProps {
    control: Control<z.infer<typeof createBatchLinkFormSchema>>;
}

export function BatchUrlForm({ control }: BatchUrlFormProps) {
    return (
        <>
            <Controller
                name="urls"
                control={control}
                render={({ field, fieldState }) => (
                    <Field>
                        <FieldLabel
                            htmlFor={field.name}
                            className="font-bold text-sm"
                        >
                            Batch URLs (JSON Format)
                        </FieldLabel>
                        <Textarea
                            {...field}
                            value={
                                typeof field.value === "string"
                                    ? field.value
                                    : ""
                            }
                            onChange={(e) => field.onChange(e.target.value)}
                            id={field.name}
                            aria-invalid={fieldState.invalid}
                            className="scrollbar-none [ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden resize-none h-60 overflow-y-scroll bg-surface"
                            placeholder={`[
    {
        "name": "My Link",
        "long_url": "https://www.example1.com",
        "short_url": "custom1",
        "expiry_date": "2024-12-31T23:59:59Z"
    },
    {
        "name": "My Link 2",
        "long_url": "https://www.example2.com"
    }
]`}
                        />
                        {fieldState.invalid && (
                            <FieldError errors={[fieldState.error]} />
                        )}
                    </Field>
                )}
            />
            <Separator />
        </>
    );
}
