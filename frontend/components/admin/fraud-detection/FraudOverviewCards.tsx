"use client";
import { Card, CardContent } from "@/components/ui/card";
import { FlagIcon, TriangleAlert } from "lucide-react";

export default function FraudOverviewCards({
  total_incidents,
  flagged_urls,
  risk_score,
}: {
  total_incidents: number | unknown;
  flagged_urls: number | unknown;
  risk_score: string | unknown;
}) {
  const cardsData = [
    {
      title: "Total Incidents",
      value: total_incidents as number,
      icon: <TriangleAlert className="h-5 w-5" />,
    },
    {
      title: "Flagged URLs",
      value: flagged_urls as number,
      icon: <FlagIcon className="h-5 w-5" />,
    },
    {
      title: "Risk Score",
      value: risk_score as string,
      icon: null,
    },
  ];

  return (
    <div className="flex flex-row justify-between gap-4">
      {cardsData.map((card) => (
        <Card key={card.title} className="w-full">
          <CardContent className="flex flex-col gap-8">
            <div className="flex justify-between">
              <span className="text-xs font-medium text-text-muted">
                {card.title}
              </span>
              <div className="flex items-center gap-2">{card.icon}</div>
            </div>
            <h2 className="text-2xl font-bold uppercase">{card.value}</h2>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
