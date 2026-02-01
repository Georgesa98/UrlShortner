"use client";
import { GetAuditLogsResponse } from "@/api-types";
import { auditTrailsColumns } from "@/components/tables/audit/columns";
import { AuditDataTable } from "@/components/tables/audit/data-table";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export default function AuditLogsClient({
  logs,
}: {
  logs: GetAuditLogsResponse;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function handlePageChange(page: number) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", page.toString());
    router.push(`${pathname}?${params.toString()}`);
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audi Trails</h1>
        <span className="text-md text-muted-foreground">
          Review security event, user actions and system activity logs.
        </span>
      </div>
      <AuditDataTable
        columns={auditTrailsColumns}
        data={logs.data}
        pagination={logs.pagination}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
