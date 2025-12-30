"use client";

import Features from "@/components/landing-page/Features";
import GetStarted from "@/components/landing-page/GetStarted";
import HeroSection from "@/components/landing-page/HeroSection";
import "@/components/landing-page/style.css";
import { Separator } from "@/components/ui/separator";
export default function LandingPage() {
    return (
        <div className="flex flex-col items-center">
            <HeroSection className="my-28" />
            <Separator />
            <Features className="my-20 px-8" />
            <Separator />
            <GetStarted className="py-20 bg-background/10" />
            <Separator />
        </div>
    );
}
