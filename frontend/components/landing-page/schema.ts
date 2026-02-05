import * as z from "zod";

export const landingPageSingleUrlSchema = z.object({
  long_url: z.string().url("Please enter a valid URL").refine((url) => url.startsWith("http"), {
    message: "URL must start with http:// or https://",
  }),
  short_url: z.string().min(3, "Custom alias must be at least 3 characters").max(64, "Custom alias is too long").optional().or(z.literal("")),
  expiry_date: z.string().optional().or(z.literal("")),
});

export const landingPageBatchUrlSchema = z.object({
  urls: z.string().min(1, "Please enter at least one URL"),
});
