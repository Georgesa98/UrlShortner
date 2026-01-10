import Link from "next/link";
import {
    NavigationMenu,
    NavigationMenuItem,
    NavigationMenuLink,
} from "../ui/navigation-menu";
import { Button } from "../ui/button";
import { Separator } from "../ui/separator";
import { useEffect, useState } from "react";
import { getAuthStatus } from "@/lib/authStatus";

export default function Navbar() {
    const [auth, setAuth] = useState<any>();
    useEffect(() => {
        async function checkAuth() {
            const status = await getAuthStatus();
            setAuth(status);
        }
        checkAuth();
    }, []);
    console.log(auth);

    return (
        <>
            <NavigationMenu className="flex flex-row min-w-full py-3 px-6 justify-between w-full ">
                <section className="flex">
                    <NavigationMenuItem>
                        <NavigationMenuLink asChild>
                            <Link href="/" className="font-bold">
                                Shortener
                            </Link>
                        </NavigationMenuLink>
                    </NavigationMenuItem>
                </section>
                <section className="flex flex-1 justify-center gap-2">
                    <NavigationMenuItem>
                        <NavigationMenuLink asChild>
                            <Link href="#" className="text-muted-foreground">
                                Home
                            </Link>
                        </NavigationMenuLink>
                    </NavigationMenuItem>
                    <NavigationMenuItem>
                        <NavigationMenuLink asChild>
                            <Link href="#" className="text-muted-foreground">
                                Contact
                            </Link>
                        </NavigationMenuLink>
                    </NavigationMenuItem>
                    <NavigationMenuItem>
                        <NavigationMenuLink asChild>
                            <Link href="#" className="text-muted-foreground">
                                About
                            </Link>
                        </NavigationMenuLink>
                    </NavigationMenuItem>
                </section>
                <section className="flex gap-2">
                    {auth?.isLoggedIn ? (
                        <NavigationMenuItem>
                            <NavigationMenuLink asChild>
                                <Link href="/dashboard">
                                    <Button className="px-4 border-2">
                                        Dashboard
                                    </Button>
                                </Link>
                            </NavigationMenuLink>
                        </NavigationMenuItem>
                    ) : (
                        <>
                            <NavigationMenuItem>
                                <NavigationMenuLink asChild>
                                    <Link href="/login">
                                        <Button
                                            className="px-4 border-2"
                                            variant="outline"
                                        >
                                            Login
                                        </Button>
                                    </Link>
                                </NavigationMenuLink>
                            </NavigationMenuItem>
                            <NavigationMenuItem>
                                <NavigationMenuLink asChild>
                                    <Link href="/signup">
                                        <Button className="px-4">Signup</Button>
                                    </Link>
                                </NavigationMenuLink>
                            </NavigationMenuItem>
                        </>
                    )}
                </section>
            </NavigationMenu>
            <Separator />
        </>
    );
}
