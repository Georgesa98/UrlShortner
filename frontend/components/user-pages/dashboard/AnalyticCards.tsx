import { Card, CardContent } from "@/components/ui/card";

const cardsData = [
    { title: "Total Clicks", value: 12450 },
    { title: "Active Links", value: 40 },
    { title: "Top Referrer", value: "Twitter" },
];
export default function AnalyticCards() {
    return (
        <section className="flex w-full justify-between gap-4">
            {cardsData.map((item) => {
                return (
                    <Card key={item.title} className="w-full">
                        <CardContent className="flex flex-col gap-4">
                            <h5 className="text-xs text-muted-foreground">
                                {item.title}
                            </h5>
                            <h2 className="text-2xl font-bold ">
                                {item.value}
                            </h2>
                        </CardContent>
                    </Card>
                );
            })}
        </section>
    );
}
