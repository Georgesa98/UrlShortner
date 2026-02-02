import { GetUserStatsResponse } from "@/api-types";
import { Card, CardContent } from "@/components/ui/card";

export default function AnalyticCards({
  userStats,
}: {
  userStats: GetUserStatsResponse;
}) {
  const cardsData = [
    { title: "Total Clicks", value: userStats.total_clicks || 0 },
    { title: "Active Links", value: userStats.active_links || 0 },
    { title: "Top Referrer", value: userStats.top_referrer || "N/A" },
  ];
  return (
    <section className="flex w-full justify-between gap-4">
      {cardsData.map((item) => {
        return (
          <Card key={item.title} className="w-full">
            <CardContent className="flex flex-col gap-4">
              <h5 className="text-xs text-muted-foreground">{item.title}</h5>
              <h2 className="text-2xl font-bold ">{item.value}</h2>
            </CardContent>
          </Card>
        );
      })}
    </section>
  );
}
