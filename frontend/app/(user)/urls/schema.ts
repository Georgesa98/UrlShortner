import * as z from "zod";

// Redirection rule schema
export const redirectionRuleSchema = z.object({
  id: z.string().optional(),
  name: z.string().min(1, "Rule name is required").max(255),
  target_url: z.string().url("Please enter a valid URL"),
  priority: z.number().int().min(0),
  is_active: z.boolean(),
  conditions: z
    .object({
      country: z.array(z.string()).optional(),
      device_type: z.array(z.enum(["mobile", "desktop", "tablet"])).optional(),
      os: z.array(z.string()).optional(),
      browser: z.array(z.string()).optional(),
      referer: z.string().optional(),
      time_range: z
        .object({
          start: z
            .string()
            .regex(/^\d{2}:\d{2}$/, "Invalid time format (HH:MM)"),
          end: z.string().regex(/^\d{2}:\d{2}$/, "Invalid time format (HH:MM)"),
        })
        .optional(),
    })
    .optional(),
});

export const createLinkFormSchema = z.object({
  name: z.string().min(1).max(256),
  long_url: z.url().refine((url) => url.toString().startsWith("http"), {
    message: "please enter a valid url",
  }),
  short_url: z.string().min(8).max(64).optional(),
  expiry_date: z.date().optional(),
  redirection_rules: z.array(redirectionRuleSchema).optional(),
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
            }`,
          );
        }
      }
      return val;
    },
    z
      .array(
        z.object({
          name: z.string().min(1).max(256),
          long_url: z.url().refine((url) => url.toString().startsWith("http"), {
            message: "please enter a valid url",
          }),
          short_url: z.string().min(8).max(64).optional(),
          expiry_date: z.date().optional(),
          password_protection: z.boolean().optional(),
          enable_tracking: z.boolean().optional(),
        }),
      )
      .min(1, { message: "At least one URL is required" })
      .max(100, { message: "Maximum 100 URLs allowed" }),
  ),
});
