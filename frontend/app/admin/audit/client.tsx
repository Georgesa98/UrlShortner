"use client";
import { GetAuditLogsResponse } from "@/api-types";
import { auditTrailsColumns } from "@/components/tables/audit/columns";
import { AuditDataTable } from "@/components/tables/audit/data-table";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { DatePicker } from "@/components/ui/datePicker";
import { Search, Calendar } from "lucide-react";
import "@/components/landing-page/style.css";

export default function AuditLogsClient({
  logs,
}: {
  logs: GetAuditLogsResponse;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [dateFrom, setDateFrom] = useState<Date | undefined>(
    searchParams.get("date_from")
      ? new Date(parseInt(searchParams.get("date_from")!))
      : undefined,
  );
  const [dateTo, setDateTo] = useState<Date | undefined>(
    searchParams.get("date_to")
      ? new Date(parseInt(searchParams.get("date_to")!))
      : undefined,
  );

  const isInitialMount = useRef(true);

  function handlePageChange(page: number) {
    const params = new URLSearchParams(searchParams.toString());
    params.set("page", page.toString());
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  }

  function handleActionChange(newAction: string) {
    const params = new URLSearchParams(searchParams.toString());
    if (newAction === "ALL") {
      params.delete("action");
    } else {
      params.set("action", newAction);
    }
    params.set("page", "1");
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  }

  function handleDateFromChange(date: Date | undefined) {
    setDateFrom(date);
    const params = new URLSearchParams(searchParams.toString());
    if (date) {
      params.set("date_from", date.getTime().toString());
    } else {
      params.delete("date_from");
    }
    params.set("page", "1");
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  }

  function handleDateToChange(date: Date | undefined) {
    setDateTo(date);
    const params = new URLSearchParams(searchParams.toString());
    if (date) {
      params.set("date_to", date.getTime().toString());
    } else {
      params.delete("date_to");
    }
    params.set("page", "1");
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  }

  return (
    <div className="p-6 space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Audit Trails</h1>
        <span className="text-md text-muted-foreground">
          Review security event, user actions and system activity logs.
        </span>
      </div>

      {/* Filters */}
      <div className="bg-surface rounded-xl p-4 flex items-center gap-4 flex-wrap">
        <Select
          value={searchParams.get("action") || "ALL"}
          onValueChange={handleActionChange}
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="All Actions" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL">All Actions</SelectItem>
            <SelectItem value="CREATE">CREATE</SelectItem>
            <SelectItem value="UPDATE">UPDATE</SelectItem>
            <SelectItem value="DELETE">DELETE</SelectItem>
            <SelectItem value="GET">GET</SelectItem>
          </SelectContent>
        </Select>

        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <DatePicker value={dateFrom} onChange={handleDateFromChange} />
        </div>

        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-muted-foreground" />
          <DatePicker value={dateTo} onChange={handleDateToChange} />
        </div>
      </div>

      {/* Data Table */}
      <AuditDataTable
        columns={auditTrailsColumns}
        data={logs.data}
        pagination={logs.pagination}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
