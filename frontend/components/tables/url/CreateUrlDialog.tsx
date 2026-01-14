import {
    createBatchLinkFormSchema,
    createLinkFormSchema,
} from "@/app/(user)/urls/schema";
import {
    batchShortenUrlAction,
    createShortUrlAction,
} from "@/app/(user)/urls/server";
import { Button } from "@/components/ui/button";
import { DatePicker } from "@/components/ui/datePicker";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import useHostname from "@/hooks/useHostname";
import { zodResolver } from "@hookform/resolvers/zod";
import { TabsContent, TabsList } from "@radix-ui/react-tabs";
import { Link, Plus } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

export default function CreateUrlDialog({
    buttonClassName,
}: {
    buttonClassName: string;
}) {
    const [activeTab, setActiveTab] = useState<string>("single");
    const hostname = useHostname();
    const router = useRouter();
    const batchUrlForm = useForm({
        resolver: zodResolver(createBatchLinkFormSchema),
        defaultValues: {
            urls: "" as any,
        },
    });
    const singleUrlForm = useForm<z.infer<typeof createLinkFormSchema>>({
        resolver: zodResolver(createLinkFormSchema),
        defaultValues: {
            name: "",
            long_url: "",
            short_url: "",
            expiry_date: new Date(),
        },
    });
    const onSubmitSingle = async (
        data: z.infer<typeof createLinkFormSchema>
    ) => {
        const { message, status } = await createShortUrlAction({
            name: data.name || "",
            long_url: data.long_url,
            short_url: data.short_url || "",
            expiry_date: data.expiry_date?.toISOString() || "",
        });
        if (status === 201) {
            toast.success("Link created successfully");
            setTimeout(() => {
                router.refresh();
            }, 2000);
        } else {
            toast.error(message || "Failed to create link");
        }
    };
    const onSubmitBatch = async (
        data: z.infer<typeof createBatchLinkFormSchema>
    ) => {
        const urlsToSubmit = data.urls.map((url) => ({
            name: url.name || "",
            long_url: url.long_url,
            short_url: url.short_url || "",
            expiry_date: url.expiry_date?.toISOString() || "",
        }));
        const { message, status } = await batchShortenUrlAction({
            data: urlsToSubmit,
        });
        if (status === 201) {
            toast.success("Batch links created successfully");
            setTimeout(() => {
                router.refresh();
            }, 2000);
        } else {
            toast.error(message || "Failed to create batch links");
        }
    };
    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button className={buttonClassName}>
                    <Plus />
                    Create New
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader className="gap-1">
                    <h1 className="text-2xl font-bold">Create New Link</h1>
                    <p className="text-sm text-muted-foreground">
                        Shorten your long URLs and customize your links
                    </p>
                </DialogHeader>
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                    <TabsList>
                        <TabsTrigger value="single">Single</TabsTrigger>
                        <TabsTrigger value="batch">Batch</TabsTrigger>
                    </TabsList>
                    <TabsContent className="flex flex-col gap-4" value="single">
                        <Separator className="w-screen" />
                        <Controller
                            name="name"
                            control={singleUrlForm.control}
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel
                                        htmlFor={field.name}
                                        className="font-bold text-sm"
                                    >
                                        Name
                                    </FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        className="h-12 text-sm"
                                        placeholder="My Link"
                                    />
                                    {fieldState.invalid && (
                                        <FieldError
                                            errors={[fieldState.error]}
                                        />
                                    )}
                                </Field>
                            )}
                        />
                        <Controller
                            name="long_url"
                            control={singleUrlForm.control}
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel
                                        htmlFor={field.name}
                                        className="font-bold text-sm"
                                    >
                                        Destination Url
                                    </FieldLabel>
                                    <div className="relative">
                                        <Input
                                            {...field}
                                            id={field.name}
                                            aria-invalid={fieldState.invalid}
                                            className="pl-8 h-12 text-sm"
                                            placeholder="http://expample.com/your-very-long-here"
                                        />
                                        <Link
                                            size={18}
                                            className="absolute left-2.5 top-1/2 text-muted-foreground -translate-y-1/2"
                                        />
                                    </div>
                                    {fieldState.invalid && (
                                        <FieldError
                                            errors={[fieldState.error]}
                                        />
                                    )}
                                </Field>
                            )}
                        />
                        <span className="font-bold text-muted-foreground text-sm">
                            Advance Options
                        </span>
                        <Separator />
                        <section className="w-full flex justify-between gap-4">
                            <Controller
                                name="short_url"
                                control={singleUrlForm.control}
                                render={({ field, fieldState }) => (
                                    <Field>
                                        <FieldLabel
                                            htmlFor={field.name}
                                            className="font-bold text-sm"
                                        >
                                            Custom Alias (Optional)
                                        </FieldLabel>
                                        <div className="relative">
                                            <span className="text-xs absolute -translate-y-1/2 top-1/2 left-2 text-muted-foreground">
                                                {hostname}/
                                            </span>
                                            <Separator
                                                orientation="vertical"
                                                className="absolute -translate-y-1/2 top-1/2 left-17"
                                            />

                                            <Input
                                                {...field}
                                                id={field.name}
                                                aria-invalid={
                                                    fieldState.invalid
                                                }
                                                className="pl-18 text-sm"
                                                placeholder="your-alias"
                                            />
                                            {fieldState.invalid && (
                                                <FieldError
                                                    errors={[fieldState.error]}
                                                />
                                            )}
                                        </div>
                                    </Field>
                                )}
                            />
                            <Controller
                                name="expiry_date"
                                control={singleUrlForm.control}
                                render={({ field, fieldState }) => (
                                    <Field>
                                        <FieldLabel
                                            htmlFor={field.name}
                                            className="font-bold text-sm"
                                        >
                                            Expiration Date
                                        </FieldLabel>
                                        <DatePicker
                                            {...field}
                                            id={field.name}
                                            aria-invalid={fieldState.invalid}
                                        />
                                        {fieldState.invalid && (
                                            <FieldError
                                                errors={[fieldState.error]}
                                            />
                                        )}
                                    </Field>
                                )}
                            />
                        </section>
                        <Separator />
                    </TabsContent>
                    <TabsContent value="batch" className="flex flex-col gap-4">
                        <Separator className="w-screen" />
                        <Controller
                            name="urls"
                            control={batchUrlForm.control}
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
                                        onChange={(e) =>
                                            field.onChange(e.target.value)
                                        }
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        className="scrollbar-none [ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden resize-none max-w-115 h-60 overflow-y-scroll"
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
                                        <FieldError
                                            errors={[fieldState.error]}
                                        />
                                    )}
                                </Field>
                            )}
                        />
                        <Separator />
                    </TabsContent>
                </Tabs>
                <div className="place-self-end flex items-center">
                    <Button size="lg" variant="ghost">
                        Cancel
                    </Button>
                    <Button
                        size="lg"
                        onClick={
                            activeTab === "single"
                                ? singleUrlForm.handleSubmit(onSubmitSingle)
                                : batchUrlForm.handleSubmit(onSubmitBatch)
                        }
                    >
                        Create Link
                    </Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}
