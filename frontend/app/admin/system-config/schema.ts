import * as z from "zod";

export const systemConfigSchema = z.object({
  // Security & Rate Limiting
  rate_limit_ip: z
    .string()
    .min(1, "Rate limit is required")
    .regex(
      /^\d+\/(second|minute|hour|day)$/,
      "Format must be: number/period (e.g., 100/hour)"
    ),
  rate_limit_user: z
    .string()
    .min(1, "Rate limit is required")
    .regex(
      /^\d+\/(second|minute|hour|day)$/,
      "Format must be: number/period (e.g., 1000/hour)"
    ),
  jwt_access_token_minutes: z.coerce
    .number({
      required_error: "JWT access token minutes is required",
      invalid_type_error: "Must be a number",
    })
    .min(1, "Must be at least 1 minute")
    .int("Must be a whole number"),

  // Shortening Logic
  short_code_length: z.coerce
    .number({
      required_error: "Short code length is required",
      invalid_type_error: "Must be a number",
    })
    .min(4, "Minimum length is 4 characters")
    .max(128, "Maximum length is 128 characters")
    .int("Must be a whole number"),
  short_code_pool_size: z.coerce
    .number({
      required_error: "Pool size is required",
      invalid_type_error: "Must be a number",
    })
    .min(1, "Must be at least 1")
    .int("Must be a whole number"),

  // Analytics & Limits
  analytics_track_ip: z.boolean({
    required_error: "Analytics IP tracking setting is required",
  }),
  max_urls_per_user: z.coerce
    .number({
      required_error: "Max URLs per user is required",
      invalid_type_error: "Must be a number",
    })
    .min(1, "Must be at least 1")
    .int("Must be a whole number"),
  url_mapping_cache_timeout: z.coerce
    .number({
      required_error: "Cache timeout is required",
      invalid_type_error: "Must be a number",
    })
    .min(0, "Must be at least 0 seconds")
    .int("Must be a whole number"),
});

export type SystemConfigFormData = z.infer<typeof systemConfigSchema>;
