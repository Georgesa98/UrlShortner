import * as z from "zod";
export const signupFormSchema = z
    .object({
        email: z.email(),
        username: z
            .string()
            .min(4, "username must be at least 4 characters")
            .max(64, "user name must be less than 64 character"),
        password: z
            .string()
            .min(8, "password must be at least 8 characters")
            .max(32, "password must be less than 32 character ")
            .regex(/\d/, "password must contain at least one number"),
        rePassword: z.string(),
        terms: z.boolean().refine((value) => value === true, {
            message: "you must accept terms and conditions",
        }),
    })
    .refine((data) => data.password === data.rePassword, {
        message: "passwords don't match",
        path: ["rePassword"],
    });
