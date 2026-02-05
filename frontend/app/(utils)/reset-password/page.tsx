"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { ArrowLeft, Check, Circle, Eye, EyeOff, RotateCcw } from "lucide-react";
import Link from "next/link";
import { Controller, useForm } from "react-hook-form";
import * as z from "zod";
import { resetPasswordFormSchema } from "./schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { resetPasswordAction } from "./server";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect } from "react";

export default function ResetPassword() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const [showPassword, setShowPassword] = useState(false);
    const [showConfirmPassword, setShowConfirmPassword] = useState(false);
    const [passwordStrength, setPasswordStrength] = useState(0);
    const [passwordStrengthLabel, setPasswordStrengthLabel] = useState("Weak");

    const uid = searchParams.get("uid");
    const token = searchParams.get("token");

    const resetForm = useForm<z.infer<typeof resetPasswordFormSchema>>({
        resolver: zodResolver(resetPasswordFormSchema),
        defaultValues: {
            new_password: "",
            re_new_password: "",
        },
        mode: "onChange",
    });

    const password = resetForm.watch("new_password");

    // Calculate password strength
    useEffect(() => {
        if (!password) {
            setPasswordStrength(0);
            setPasswordStrengthLabel("Weak");
            return;
        }

        let strength = 0;

        // Length check
        if (password.length >= 8) strength += 33;
        if (password.length >= 12) strength += 17;

        // Number check
        if (/\d/.test(password)) strength += 25;

        // Special character check
        if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength += 25;

        setPasswordStrength(strength);

        if (strength <= 33) {
            setPasswordStrengthLabel("Weak");
        } else if (strength <= 66) {
            setPasswordStrengthLabel("Medium");
        } else {
            setPasswordStrengthLabel("Strong");
        }
    }, [password]);

    const getRequirementStatus = (requirement: string) => {
        if (!password) return false;

        switch (requirement) {
            case "length":
                return password.length >= 8;
            case "number":
                return /\d/.test(password);
            case "special":
                return /[!@#$%^&*(),.?":{}|<>]/.test(password);
            default:
                return false;
        }
    };

    async function onSubmit(data: z.infer<typeof resetPasswordFormSchema>) {
        if (!uid || !token) {
            toast.error("Invalid reset link. Please request a new one.");
            return;
        }

        const result = await resetPasswordAction({
            uid,
            token,
            new_password: data.new_password,
            re_new_password: data.re_new_password,
        });

        if (result.success) {
            toast.success("Password reset successful!");
            setTimeout(() => {
                router.push("/login");
            }, 2000);
        } else {
            toast.error(result.message || "Failed to reset password");
        }
    }

    return (
        <div className="relative overflow-hidden min-w-full h-screen">
            {/* Blue Glow (Top Left/Center) */}
            <div
                className="pointer-events-none absolute top-0 left-0 w-200 h-125 opacity-20 blur-[70px]"
                style={{
                    background:
                        "radial-gradient(circle, #007bff 0%, transparent 70%)",
                }}
            />

            {/* Purple Glow (Bottom Right) */}
            <div
                className="pointer-events-none absolute bottom-0 right-0 w-200 h-125 opacity-[0.15] blur-[100px]"
                style={{
                    background:
                        "radial-gradient(circle, #a855f7 0%, transparent 70%)",
                }}
            />

            <div className="relative grid place-content-center h-full">
                <Card className="overflow-hidden p-0 w-[500px]">
                    <CardContent className="p-0">
                        <div className="flex flex-col items-center w-full px-8 py-8 gap-6">
                            {/* Header */}
                            <div className="flex flex-col items-center gap-2">
                                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center mb-2">
                                    <RotateCcw className="w-6 h-6 text-brand-blue" />
                                </div>
                                <h1 className="text-2xl font-bold">
                                    Reset Your Password
                                </h1>
                                <p className="text-sm text-muted-foreground text-center">
                                    Enter your new password below. Make sure
                                    it&apos;s secure.
                                </p>
                            </div>

                            {/* New Password Field */}
                            <div className="flex flex-col gap-2 w-full">
                                <Controller
                                    control={resetForm.control}
                                    name="new_password"
                                    render={({ field, fieldState }) => (
                                        <Field>
                                            <FieldLabel htmlFor={field.name}>
                                                New Password
                                            </FieldLabel>
                                            <div className="relative">
                                                <Input
                                                    {...field}
                                                    id={field.name}
                                                    aria-invalid={
                                                        fieldState.invalid
                                                    }
                                                    placeholder="Enter new password"
                                                    type={
                                                        showPassword
                                                            ? "text"
                                                            : "password"
                                                    }
                                                    className="pr-10"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        setShowPassword(
                                                            !showPassword
                                                        )
                                                    }
                                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                                >
                                                    {showPassword ? (
                                                        <EyeOff className="w-4 h-4" />
                                                    ) : (
                                                        <Eye className="w-4 h-4" />
                                                    )}
                                                </button>
                                            </div>
                                            {fieldState.invalid && (
                                                <FieldError
                                                    errors={[fieldState.error]}
                                                />
                                            )}
                                        </Field>
                                    )}
                                />
                            </div>

                            {/* Confirm Password Field */}
                            <div className="flex flex-col gap-2 w-full">
                                <Controller
                                    control={resetForm.control}
                                    name="re_new_password"
                                    render={({ field, fieldState }) => (
                                        <Field>
                                            <FieldLabel htmlFor={field.name}>
                                                Confirm New Password
                                            </FieldLabel>
                                            <div className="relative">
                                                <Input
                                                    {...field}
                                                    id={field.name}
                                                    aria-invalid={
                                                        fieldState.invalid
                                                    }
                                                    placeholder="Re-enter new password"
                                                    type={
                                                        showConfirmPassword
                                                            ? "text"
                                                            : "password"
                                                    }
                                                    className="pr-10"
                                                />
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        setShowConfirmPassword(
                                                            !showConfirmPassword
                                                        )
                                                    }
                                                    className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                                                >
                                                    {showConfirmPassword ? (
                                                        <EyeOff className="w-4 h-4" />
                                                    ) : (
                                                        <Eye className="w-4 h-4" />
                                                    )}
                                                </button>
                                            </div>
                                            {fieldState.invalid && (
                                                <FieldError
                                                    errors={[fieldState.error]}
                                                />
                                            )}
                                        </Field>
                                    )}
                                />
                            </div>

                            {/* Password Strength Meter */}
                            <div className="w-full">
                                <div className="flex justify-between items-center mb-2">
                                    <span className="text-xs font-medium text-muted-foreground">
                                        STRENGTH
                                    </span>
                                    <span
                                        className={`text-xs font-medium ${
                                            passwordStrength <= 33
                                                ? "text-orange-500"
                                                : passwordStrength <= 66
                                                  ? "text-yellow-500"
                                                  : "text-green-500"
                                        }`}
                                    >
                                        {passwordStrengthLabel}
                                    </span>
                                </div>
                                <div className="w-full h-2 bg-surface rounded-full overflow-hidden">
                                    <div
                                        className={`h-full transition-all duration-300 ${
                                            passwordStrength <= 33
                                                ? "bg-orange-500"
                                                : passwordStrength <= 66
                                                  ? "bg-yellow-500"
                                                  : "bg-green-500"
                                        }`}
                                        style={{
                                            width: `${passwordStrength}%`,
                                        }}
                                    />
                                </div>
                            </div>

                            {/* Password Requirements */}
                            <div className="w-full bg-surface/50 rounded-lg p-4">
                                <p className="text-xs font-medium text-muted-foreground mb-3">
                                    PASSWORD REQUIREMENTS:
                                </p>
                                <div className="space-y-2">
                                    <div className="flex items-center gap-2">
                                        {getRequirementStatus("length") ? (
                                            <Check className="w-4 h-4 text-green-500" />
                                        ) : (
                                            <Circle className="w-4 h-4 text-muted-foreground" />
                                        )}
                                        <span
                                            className={`text-sm ${
                                                getRequirementStatus("length")
                                                    ? "text-green-500"
                                                    : "text-muted-foreground"
                                            }`}
                                        >
                                            At least 8 characters long
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {getRequirementStatus("number") ? (
                                            <Check className="w-4 h-4 text-green-500" />
                                        ) : (
                                            <Circle className="w-4 h-4 text-muted-foreground" />
                                        )}
                                        <span
                                            className={`text-sm ${
                                                getRequirementStatus("number")
                                                    ? "text-green-500"
                                                    : "text-muted-foreground"
                                            }`}
                                        >
                                            Contains at least one number
                                        </span>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        {getRequirementStatus("special") ? (
                                            <Check className="w-4 h-4 text-green-500" />
                                        ) : (
                                            <Circle className="w-4 h-4 text-muted-foreground" />
                                        )}
                                        <span
                                            className={`text-sm ${
                                                getRequirementStatus("special")
                                                    ? "text-green-500"
                                                    : "text-muted-foreground"
                                            }`}
                                        >
                                            Contains at least one special
                                            character
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Reset Password Button */}
                            <Button
                                className="w-full"
                                onClick={resetForm.handleSubmit(onSubmit)}
                                disabled={!resetForm.formState.isValid}
                            >
                                Reset Password
                            </Button>

                            {/* Back to Login Link */}
                            <Link
                                href="/login"
                                className="flex items-center gap-2 text-sm text-muted-foreground hover:text-brand-blue transition-colors"
                            >
                                <ArrowLeft className="w-4 h-4" />
                                Back to Log In
                            </Link>

                            {/* Footer */}
                            <p className="text-xs text-muted-foreground text-center mt-2">
                                © 2024 URL Shortener Service. Secure
                                Connection.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
