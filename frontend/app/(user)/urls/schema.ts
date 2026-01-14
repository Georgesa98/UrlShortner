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
    urls: z.preprocess(
        (val) => {
            if (typeof val === "string") {
                try {
                    const parsed = JSON.parse(val);
                    if (Array.isArray(parsed)) {
                        return parsed.map((item) => ({
                            ...item,
                            expiry_date: item.expiry_date
                                ? new Date(item.expiry_date)
                                : undefined,
                        }));
                    }
                    throw new Error("Parsed value is not an array");
                } catch (e) {
                    throw new Error(
                        `Invalid JSON format: ${
                            e instanceof Error ? e.message : "Unknown error"
                        }`
                    );
                }
            }
            return val;
        },
        z
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
            .min(1, { message: "At least one URL is required" })
            .max(100, { message: "Maximum 100 URLs allowed" })
    ),
});
