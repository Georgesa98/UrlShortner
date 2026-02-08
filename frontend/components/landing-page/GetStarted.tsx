"use client";

import Link from "next/link";
import { Button } from "../ui/button";
import { useEffect, useState } from "react";
import { getAuthStatus } from "@/lib/authStatus";

export default function GetStarted({ className }: { className?: string }) {
    const [auth, setAuth] = useState<any>();

    useEffect(() => {
        async function checkAuth() {
            const status = await getAuthStatus();
            setAuth(status);
        }
        checkAuth();
    }, []);

    return (
        <div className={`flex flex-col items-center w-full gap-8 ${className}`}>
            <h1 className="text-2xl font-bold">
                {auth?.isLoggedIn ? "Continue your journey" : "Ready to get started?"}
            </h1>
            <div className="flex gap-2 justify-center">
                {auth?.isLoggedIn ? (
                    <Link href={auth.isAdmin ? "/admin/dashboard" : "/dashboard"}>
                        <Button size="lg">Go to Dashboard</Button>
                    </Link>
                ) : (
                    <>
                        <Link href="/signup">
                            <Button size="lg">Create Free Account</Button>
                        </Link>
                        <Link href="#">
                            <Button variant="outline" size="lg">
                                Contact Us
                            </Button>
                        </Link>
                    </>
                )}
            </div>
        </div>
    );
}
