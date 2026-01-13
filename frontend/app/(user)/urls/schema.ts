import * as z from "zod";
export const createLinkFormSchema = z.object({
    name: z.string().min(1).max(256),
    long_url: z.url().refine((url) => url.toString().startsWith("http"), {
        message: "please enter a valid url",
    }),
    short_url: z.string().min(8).max(64).optional(),
    expiry_date: z.date().optional(),
});

export const createBatchLinkFormSchema = z.object({
    urls: z
        .array(
            z.object({
                name: z.string().min(1).max(256),
                long_url: z
                    .url()
                    .refine((url) => url.toString().startsWith("http"), {
                        message: "please enter a valid url",
                    }),
                short_url: z.string().min(8).max(64).optional(),
                expiry_date: z.date().optional(),
            })
        )
        .min(1)
        .max(100),
});
