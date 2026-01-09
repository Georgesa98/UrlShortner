import { createLinkFormSchema } from "@/app/(user)/urls/schema";
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
import { FileDiff, Link, Plus } from "lucide-react";
import { Controller, useForm } from "react-hook-form";
import z from "zod";

export default function CreateUrlDialog({
    buttonClassName,
}: {
    buttonClassName: string;
}) {
    const hostname = useHostname();
    const singleUrlForm = useForm<z.infer<typeof createLinkFormSchema>>({
        resolver: zodResolver(createLinkFormSchema),
        defaultValues: {
            destination: "",
            custom_alias: "",
            expiration_date: new Date(),
        },
    });
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
                <Tabs defaultValue="single">
                    <TabsList>
                        <TabsTrigger value="single">Single</TabsTrigger>
                        <TabsTrigger value="batch">Batch</TabsTrigger>
                    </TabsList>
                    <TabsContent className="flex flex-col gap-4" value="single">
                        <Separator className="w-screen" />
                        <Controller
                            name="destination"
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
                            <Field>
                                <FieldLabel>Custom Alias (Optional)</FieldLabel>
                                <div className="relative">
                                    <span className="text-xs absolute -translate-y-1/2 top-1/2 left-2 text-muted-foreground">
                                        {hostname}/
                                    </span>
                                    <Separator
                                        orientation="vertical"
                                        className="absolute -translate-y-1/2 top-1/2 left-17"
                                    />
                                    <Input
                                        className="pl-18 text-sm"
                                        placeholder="your-alias"
                                    />
                                </div>
                            </Field>
                            <Field>
                                <FieldLabel>Expiration Date</FieldLabel>
                                <DatePicker />
                            </Field>
                        </section>
                        <Separator />
                    </TabsContent>
                    <TabsContent value="batch">
                        <Textarea
                            className="scrollbar-none [ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden resize-none max-w-115 h-60 overflow-y-scroll"
                            placeholder={`[
    {
        "long_url": "https://www.example1.com",
        "short_url": "custom1",
        "expiry_date": "2024-12-31T23:59:59Z"
    },
    {
        "long_url": "https://www.example2.com",
        "short_url": "custom2"
    }
]`}
                        />
                    </TabsContent>
                </Tabs>
                <div className="place-self-end flex items-center">
                    <Button size="lg" variant="ghost">
                        Cancel
                    </Button>
                    <Button size="lg">Create Link</Button>
                </div>
            </DialogContent>
        </Dialog>
    );
}
