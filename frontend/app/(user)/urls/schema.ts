import * as z from "zod";
export const createLinkFormSchema = z.object({
    destination: z.url(),
    custom_alias: z.string().min(4).max(64).optional(),
    expiration_date: z.date().optional(),
});
