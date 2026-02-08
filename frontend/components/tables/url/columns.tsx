"use client";
import { UrlResponse } from "@/api-types";
import { formatDate } from "@/lib/formatToClientDate";
import { ColumnDef } from "@tanstack/react-table";
import { BarChart } from "lucide-react";
import { Checkbox } from "@/components/ui/checkbox";
import { ActionsCell } from "./ActionsCell";

export const columns: ColumnDef<UrlResponse>[] = [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={table.getIsAllPageRowsSelected()}
        onCheckedChange={(value) => table.toggleAllPageRowsSelected(!!value)}
        aria-label="Select all"
        className="translate-y-[2px]"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        checked={row.getIsSelected()}
        onCheckedChange={(value) => row.toggleSelected(!!value)}
        aria-label="Select row"
        className="translate-y-[2px]"
        onClick={(e) => e.stopPropagation()}
      />
    ),
    enableSorting: false,
    enableHiding: false,
  },
  {
    accessorKey: "linkInformation",
    header: "LINK INFORMATION",
    cell: ({ row }) => {
      const data = row.original;
      return (
        <div className="flex flex-col">
          <div className="flex items-center gap-2">
            <span className="font-bold">{data.name}</span>
            <span
              className={`rounded-lg px-1.5 py-0.5 text-[10px] font-bold ${
                data.url_status.state === "ACTIVE"
                  ? "bg-green-500/10 text-green-500"
                  : data.url_status.state === "EXPIRED"
                  ? "bg-yellow-500/10 text-yellow-500"
                  : data.url_status.state === "FLAGGED"
                  ? "bg-orange-500/10 text-orange-500"
                  : "bg-red-500/10 text-red-500"
              }`}
            >
              {data.url_status.state}
            </span>
          </div>
          <span className="text-sm text-blue-400">{data.short_url}</span>
          <span className="max-w-75 truncate text-xs text-muted-foreground">
            {data.long_url}
          </span>
        </div>
      );
    },
  },
  {
    accessorKey: "created_at",
    header: "CREATED AT",
    cell: ({ row }) => (
      <span className="text-muted-foreground">
        {formatDate(row.getValue("created_at"))}
      </span>
    ),
  },
  {
    accessorKey: "visits",
    header: "CLICKS",
    cell: ({ row }) => (
      <div className="flex items-center gap-2">
        <BarChart size={14} className="text-muted-foreground" />
        <span className="text-muted-foreground">{row.getValue("visits")}</span>
      </div>
    ),
  },
  {
    id: "actions",
    header: "ACTIONS",
    cell: ({ row }) => <ActionsCell data={row.original} />,
  },
];
