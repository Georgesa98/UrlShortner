"use client";

import FraudOverviewCards from "@/components/admin/fraud-detection/FraudOverviewCards";
import IncidentByTypeCard from "@/components/admin/fraud-detection/IncidentByTypeCard";
import { FraudDetectionDataTable } from "@/components/tables/fraud-detection/data-table";
import { fraudDetectionColumns } from "@/components/tables/fraud-detection/columns";
import { UrlResponse, Pagination } from "@/api-types";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export default function FraudDetectionOverview({
  data,
  incidentsTableData,
}: {
  data: Record<string, unknown>;
  incidentsTableData: {
    urls: UrlResponse[];
    pagination: Pagination;
  };
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParam = useSearchParams();

  const handlePageChange = (page: number) => {
    const params = new URLSearchParams(searchParam.toString());
    params.set("page", page.toString());
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  };

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-text-main">
          Fraud Detection Center
        </h1>
        <p className="text-text-muted mt-1">
          Monitor and analyze fraud incidents across your platform.
        </p>
      </div>
      <div className="grid grid-cols-3 grid-rows-[auto,1fr] gap-3">
        <div className="col-span-3">
          <FraudOverviewCards
            total_incidents={data.total_incidents}
            flagged_urls={data.flagged_urls}
            risk_score={data.risk_score}
          />
        </div>
        <div className="row-start-2 row-end-3 col-start-3 col-end-4">
          <IncidentByTypeCard incidents_by_type={data.incidents_by_type} />
        </div>
        <div className="col-span-2 row-start-2 row-end-3">
          <FraudDetectionDataTable
            columns={fraudDetectionColumns}
            data={incidentsTableData.urls}
            pagination={incidentsTableData.pagination}
            onPageChange={handlePageChange}
          />
        </div>
      </div>
    </div>
  );
}
