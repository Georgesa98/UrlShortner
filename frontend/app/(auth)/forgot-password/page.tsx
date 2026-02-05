"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { ArrowLeft, ArrowRight, Mail } from "lucide-react";
import Link from "next/link";
import { Controller, useForm } from "react-hook-form";
import * as z from "zod";
import { forgotPasswordFormSchema } from "./schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { forgotPasswordAction } from "./server";
import { toast } from "sonner";
import { useState } from "react";

export default function ForgotPassword() {
    const [emailSent, setEmailSent] = useState(false);

    const forgotPasswordForm = useForm<
        z.infer<typeof forgotPasswordFormSchema>
    >({
        resolver: zodResolver(forgotPasswordFormSchema),
        defaultValues: {
            email: "",
        },
    });

    async function onSubmit(data: z.infer<typeof forgotPasswordFormSchema>) {
        const result = await forgotPasswordAction({
            email: data.email,
        });

        if (result.success) {
            toast.success(
                "Password reset email sent! Check your inbox for further instructions."
            );
            setEmailSent(true);
        } else {
            toast.error(
                result.message || "Failed to send password reset email"
            );
        }
    }

    return (
        <Card className="overflow-hidden p-0">
            <CardContent className="p-0">
                <div className="flex flex-col items-center w-90 px-6 py-6 gap-6">
                    {!emailSent ? (
                        <>
                            {/* Header */}
                            <div className="flex flex-col items-center gap-2">
                                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                                    <Mail className="w-6 h-6 text-brand-blue" />
                                </div>
                                <h1 className="text-2xl font-bold">
                                    Forgot Password?
                                </h1>
                                <p className="text-xs text-muted-foreground text-center">
                                    No worries! Enter your email and we&apos;ll
                                    send you reset instructions.
                                </p>
                            </div>

                            {/* Email Field */}
                            <div className="flex flex-col gap-2 w-full">
                                <Controller
                                    control={forgotPasswordForm.control}
                                    name="email"
                                    render={({ field, fieldState }) => (
                                        <Field>
                                            <FieldLabel htmlFor={field.name}>
                                                Email Address
                                            </FieldLabel>
                                            <Input
                                                {...field}
                                                id={field.name}
                                                aria-invalid={fieldState.invalid}
                                                placeholder="name@example.com"
                                                type="email"
                                            />
                                            {fieldState.invalid && (
                                                <FieldError
                                                    errors={[fieldState.error]}
                                                />
                                            )}
                                        </Field>
                                    )}
                                />
                            </div>

                            {/* Send Reset Link Button */}
                            <Button
                                className="w-full"
                                onClick={forgotPasswordForm.handleSubmit(
                                    onSubmit
                                )}
                            >
                                Send Reset Link <ArrowRight />
                            </Button>
                        </>
                    ) : (
                        <>
                            {/* Success State */}
                            <div className="flex flex-col items-center gap-2">
                                <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center mb-2">
                                    <Mail className="w-6 h-6 text-green-500" />
                                </div>
                                <h1 className="text-2xl font-bold">
                                    Check Your Email
                                </h1>
                                <p className="text-xs text-muted-foreground text-center">
                                    We&apos;ve sent password reset instructions
                                    to{" "}
                                    <span className="text-brand-blue font-medium">
                                        {forgotPasswordForm.getValues("email")}
                                    </span>
                                </p>
                            </div>

                            {/* Instructions */}
                            <div className="w-full bg-surface/50 rounded-lg p-4">
                                <p className="text-xs text-muted-foreground mb-2">
                                    What to do next:
                                </p>
                                <ul className="space-y-2 text-xs text-muted-foreground">
                                    <li className="flex gap-2">
                                        <span className="text-brand-blue">
                                            1.
                                        </span>
                                        Check your email inbox
                                    </li>
                                    <li className="flex gap-2">
                                        <span className="text-brand-blue">
                                            2.
                                        </span>
                                        Click the reset link in the email
                                    </li>
                                    <li className="flex gap-2">
                                        <span className="text-brand-blue">
                                            3.
                                        </span>
                                        Create your new password
                                    </li>
                                </ul>
                            </div>

                            {/* Resend Email Button */}
                            <Button
                                variant="outline"
                                className="w-full"
                                onClick={() => {
                                    setEmailSent(false);
                                    forgotPasswordForm.reset();
                                }}
                            >
                                Didn&apos;t receive the email? Try again
                            </Button>
                        </>
                    )}
                </div>
                <Separator />
                <div className="w-full text-muted-foreground text-xs p-4 flex items-center justify-center">
                    <Link
                        href="/login"
                        className="flex items-center gap-2 hover:text-brand-blue transition-colors"
                    >
                        <ArrowLeft className="w-3 h-3" />
                        Back to Log In
                    </Link>
                </div>
            </CardContent>
        </Card>
    );
}
