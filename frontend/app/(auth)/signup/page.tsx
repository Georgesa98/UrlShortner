"use client";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { ArrowRight } from "lucide-react";
import { Controller, useForm } from "react-hook-form";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { signupFormSchema } from "./schema";
import Image from "next/image";
import Link from "next/link";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { signupAction } from "./server";
import { toast } from "sonner";
import { redirect } from "next/navigation";
export default function Signup() {
    const signupForm = useForm<z.infer<typeof signupFormSchema>>({
        resolver: zodResolver(signupFormSchema),
        defaultValues: {
            email: "",
            username: "",
            password: "",
            rePassword: "",
            terms: false,
        },
    });
    async function onSubmit(data: z.infer<typeof signupFormSchema>) {
        const result = await signupAction(data);
        if (result.success && result.status === 201) {
            toast.success("Account has been created");
            setTimeout(() => {
                redirect("/");
            }, 2000);
        } else {
            toast.error(result.message || "An error has occurred");
            console.error(result);
        }
    }
    return (
        <Card className="overflow-hidden p-0">
            <CardContent className="p-0">
                <div className="flex flex-col items-center w-90 px-6 py-6 gap-4">
                    <div className="flex flex-col items-center gap-2">
                        <h1 className="text-2xl font-bold">
                            Create an Account
                        </h1>
                        <p className="text-xs text-muted-foreground">
                            Start shortening your links, track analysis, and
                            more.
                        </p>
                    </div>
                    <div className="flex flex-col gap-2 w-full">
                        <Controller
                            control={signupForm.control}
                            name="email"
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel htmlFor={field.name}>
                                        Email
                                    </FieldLabel>
                                    <Input
                                        {...field}
                                        type="email"
                                        aria-invalid={fieldState.invalid}
                                        id={field.name}
                                        placeholder="name@example.com"
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
                    <div className="flex flex-col gap-2 w-full">
                        <Controller
                            control={signupForm.control}
                            name="username"
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel htmlFor={field.name}>
                                        Username
                                    </FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        placeholder="John doe"
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
                    <div className="flex flex-col gap-2 w-full">
                        <Controller
                            control={signupForm.control}
                            name="password"
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel htmlFor={field.name}>
                                        Password
                                    </FieldLabel>
                                    <Input
                                        {...field}
                                        aria-invalid={fieldState.invalid}
                                        id={field.name}
                                        placeholder="password"
                                        type="password"
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
                    <div className="flex flex-col gap-2 w-full">
                        <Controller
                            control={signupForm.control}
                            name="rePassword"
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel htmlFor={field.name}>
                                        Confirm Password
                                    </FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        placeholder="confirm password"
                                        type="password"
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
                    <div>
                        <Controller
                            name="terms"
                            control={signupForm.control}
                            render={({ field, fieldState }) => (
                                <Field className="flex flex-row items-center gap-2 w-full">
                                    <Input
                                        checked={field.value}
                                        onChange={(e) =>
                                            field.onChange(e.target.checked)
                                        }
                                        onBlur={field.onBlur}
                                        ref={field.ref}
                                        type="checkbox"
                                        className="w-4 h-4"
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                    />
                                    <FieldLabel
                                        htmlFor={field.name}
                                        className="text-muted-foreground min-w-[90%] text-xs"
                                    >
                                        I agree to the terms of service and
                                        privacy policy
                                    </FieldLabel>
                                    {fieldState.invalid && (
                                        <FieldError
                                            errors={[fieldState.error]}
                                        />
                                    )}
                                </Field>
                            )}
                        />
                    </div>
                    <Button
                        className="w-full"
                        onClick={signupForm.handleSubmit(onSubmit)}
                    >
                        Create Account <ArrowRight />
                    </Button>
                    <div className="relative w-full">
                        <span className="absolute left-19 -top-1.5 bg-card px-4  text-muted-foreground text-xs">
                            OR CONTINUE WITH
                        </span>
                        <Separator />
                    </div>
                    <div className="flex justify-between gap-4 w-full">
                        <Button
                            variant="outline"
                            className="bg-transparent flex-1 w-full"
                        >
                            <Image
                                src="google.svg"
                                width={16}
                                height={16}
                                alt="google"
                            />
                            Google
                        </Button>
                        <Button
                            variant="outline"
                            className="bg-transparent flex-1"
                        >
                            <Image
                                src="github.svg"
                                className=""
                                width={20}
                                height={20}
                                alt="github"
                            />
                            Github
                        </Button>
                    </div>
                </div>
                <Separator />
                <div className="w-full text-muted-foreground text-xs p-4 flex items-center justify-center ">
                    <p>
                        Already have an account?{" "}
                        <span className="text-brand-blue">
                            <Link href="/login">Log In</Link>
                        </span>
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
