import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { ArrowRight } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

export default function Signup() {
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
                        <Label>Email</Label>
                        <Input placeholder="name@example.com" />
                    </div>
                    <div className="flex flex-col gap-2 w-full">
                        <Label>Username</Label>
                        <Input placeholder="John doe" />
                    </div>
                    <div className="flex flex-col gap-2 w-full">
                        <Label>Password</Label>
                        <Input placeholder="password" type="password" />
                    </div>
                    <div className="flex flex-col gap-2 w-full">
                        <Label>Confirm Password</Label>
                        <Input placeholder="password" type="password" />
                    </div>
                    <div className="flex gap-2">
                        <Input type="checkbox" className="w-4 h-4" />
                        <span className="text-muted-foreground text-xs :accent-background">
                            I agree to the terms of service and privacy policy
                        </span>
                    </div>
                    <Button className="w-full">
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
