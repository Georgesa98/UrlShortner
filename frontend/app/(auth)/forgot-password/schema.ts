import * as z from "zod";

export const forgotPasswordFormSchema = z.object({
    email: z.string().email("please enter a valid email address"),
});

export type ForgotPasswordFormData = z.infer<typeof forgotPasswordFormSchema>;
