import Link from "next/link";
import { Button } from "../ui/button";

export default function GetStarted({ className }: { className?: string }) {
    return (
        <div className={`flex flex-col items-center w-full gap-8 ${className}`}>
            <h1 className="text-2xl font-bold">Ready to get started?</h1>
            <div className="flex gap-2 justify-center">
                <Link href="/signup">
                    <Button size="lg">Create Free Account</Button>
                </Link>
                <Link href="#">
                    <Button variant="outline" size="lg">
                        Contact Us
                    </Button>
                </Link>
            </div>
        </div>
    );
}
