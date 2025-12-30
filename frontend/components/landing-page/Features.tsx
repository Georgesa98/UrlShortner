import { ChartArea, LayoutGrid, Link } from "lucide-react";
import { Card, CardContent } from "../ui/card";

interface FeatureCard {
    icon: React.ElementType;
    title: string;
    description: string;
}

const featureCards: FeatureCard[] = [
    {
        icon: ChartArea,
        title: "Detailed Analytics",
        description:
            "Gain insights into who is clicking your links. Track location, device type, browser, and referrer data in realtime.",
    },
    {
        icon: Link,
        title: "Url Management",
        description:
            "Need to change destination? Edit your Urls anytime without changing the link you shared.",
    },
    {
        icon: LayoutGrid,
        title: "Robust API",
        description:
            "Integrate shortening into your own application with our developer-friendly API. Documentation included.",
    },
];

export default function Features({ className }: { className?: string }) {
    return (
        <div className={`flex flex-col items-center gap-8 ${className}`}>
            <div className="flex flex-col items-center gap-2">
                <h1 className="font-bold text-3xl">
                    Powerful features for powerful users
                </h1>
                <p className="text-muted-foreground text-sm">
                    Everything you need to manage your link, track your
                    audience, and optimize your brand.
                </p>
            </div>
            <div className="flex justify-around gap-6 w-full">
                {featureCards.map((card, index) => (
                    <Card key={index} className="flex-1">
                        <CardContent className="flex flex-col gap-2">
                            <div className="bg-[#1d3155] w-fit rounded-xl p-3">
                                <card.icon className="text-brand-blue" />
                            </div>
                            <h2 className="font-bold">{card.title}</h2>
                            <p className="text-muted-foreground text-sm">
                                {card.description}
                            </p>
                        </CardContent>
                    </Card>
                ))}
            </div>
        </div>
    );
}
