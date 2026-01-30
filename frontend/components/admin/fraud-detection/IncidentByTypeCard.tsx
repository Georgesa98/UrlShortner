import { Card, CardContent } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";

export default function IncidentByTypeCard({
  incidents_by_type,
}: {
  incidents_by_type: {
    incident_type: string;
    count: number;
  }[];
}) {
  const total_incidents = incidents_by_type.reduce(
    (acc, curr) => acc + curr.count,
    0,
  );
  const incident_percentage = incidents_by_type.map((incident) => {
    return {
      incident_type: incident.incident_type,
      percentage: Math.round((incident.count / total_incidents) * 100),
    };
  });

  return (
    <Card>
      <CardContent>
        <div className="flex flex-col gap-6  justify-between">
          <span className="text-lg font-bold ">Incidents by Type</span>
          <div className="flex flex-col gap-2">
            {incident_percentage.map((incident, index) => {
              return (
                <div key={index} className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">
                      {incident.incident_type}
                    </span>
                    <span>{incident.percentage}%</span>
                  </div>
                  <Progress value={incident.percentage} />
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
