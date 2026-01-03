"use client";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { ArrowRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { Controller, useForm } from "react-hook-form";
import * as z from "zod";
import { loginFormSchema } from "./schema";
import { zodResolver } from "@hookform/resolvers/zod";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { loginAction } from "./server";
import { toast } from "sonner";
import { redirect } from "next/navigation";
export default function Login() {
    const loginForm = useForm<z.infer<typeof loginFormSchema>>({
        resolver: zodResolver(loginFormSchema),
        defaultValues: {
            username: "",
            password: "",
        },
    });
    async function onSubmit(data: z.infer<typeof loginFormSchema>) {
        const { message, status } = await loginAction({
            username: data.username,
            password: data.password,
        });
        if (status === 200) {
            toast.success("login successful");
            setTimeout(() => {
                redirect("/");
            }, 2000);
        } else {
            toast.error("please check your credentials");
        }
    }
    return (
        <Card className="overflow-hidden p-0">
            <CardContent className="p-0">
                <div className="flex flex-col items-center w-90 px-6 py-6 gap-6">
                    <div className="flex flex-col items-center gap-2">
                        <h1 className="text-2xl font-bold">Welcome Back</h1>
                        <p className="text-xs text-muted-foreground">
                            Enter your credentials to access your account
                        </p>
                    </div>
                    <div className="flex flex-col gap-2 w-full">
                        <Controller
                            control={loginForm.control}
                            name="username"
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel htmlFor={field.name}>
                                        Email or Username
                                    </FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
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
                            control={loginForm.control}
                            name="password"
                            render={({ field, fieldState }) => (
                                <Field>
                                    <FieldLabel htmlFor={field.name}>
                                        Password
                                    </FieldLabel>
                                    <Input
                                        {...field}
                                        id={field.name}
                                        aria-invalid={fieldState.invalid}
                                        placeholder="password"
                                        type="password"
                                    />
                                    <p className="text-brand-blue text-xs">
                                        Forgot Password?
                                    </p>
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
                        onClick={loginForm.handleSubmit(onSubmit)}
                    >
                        Sign In <ArrowRight />
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
                        Don&apos;t have an account?{" "}
                        <span className="text-brand-blue">
                            <Link href="/signup">Sign Up</Link>
                        </span>
                    </p>
                </div>
            </CardContent>
        </Card>
    );
}
