import * as z from "zod";

export const resetPasswordFormSchema = z
    .object({
        new_password: z
            .string()
            .min(8, "password must be at least 8 characters")
            .max(32, "password must be less than 32 characters")
            .regex(/\d/, "password must contain at least one number")
            .regex(
                /[!@#$%^&*(),.?":{}|<>]/,
                "password must contain at least one special character"
            ),
        re_new_password: z.string(),
    })
    .refine((data) => data.new_password === data.re_new_password, {
        message: "passwords don't match",
        path: ["re_new_password"],
    });

export type ResetPasswordFormData = z.infer<typeof resetPasswordFormSchema>;
