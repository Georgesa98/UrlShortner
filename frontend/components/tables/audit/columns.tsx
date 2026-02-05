"use client";

import { AuditLogs, GetAuditLogsResponse } from "@/api-types";
import { formatDateTime } from "@/lib/formatToClientDate";
import { ColumnDef } from "@tanstack/react-table";

export const auditTrailsColumns: ColumnDef<AuditLogs>[] = [
  {
    accessorKey: "username",
    header: "Username",
    cell: ({ row }) => {
      const data = row.original;
      return <span className="text-muted-foreground">{data.username}</span>;
    },
  },
  {
    accessorKey: "action",
    header: "Action",
    cell: ({ row }) => {
      const data = row.original;
      return <span className="text-muted-foreground">{data.action}</span>;
    },
  },
  {
    accessorKey: "timestamp",
    header: "Timestamp",
    cell: ({ row }) => {
      const data = row.original;

      return (
        <span className="text-muted-foreground">
          {formatDateTime(data.timestamp)}
        </span>
      );
    },
  },
  {
    accessorKey: "content_id",
    header: "Content Id",
    cell: ({ row }) => {
      const data = row.original;
      return <span className="text-muted-foreground">{data.content_id}</span>;
    },
  },
  {
    accessorKey: "content_type",
    header: "Content Type",
    cell: ({ row }) => {
      const data = row.original;
      return <span className="text-muted-foreground">{data.content_type}</span>;
    },
  },
  {
    accessorKey: "ip_address",
    header: "IP Address",
    cell: ({ row }) => {
      const data = row.original;
      return <span className="text-muted-foreground">{data.ip_address}</span>;
    },
  },
  {
    accessorKey: "successful",
    header: "Successful",
    cell: ({ row }) => {
      const data = row.original;
      return (
        <span className="text-muted-foreground">
          {data.successful ? "Yes" : "No"}
        </span>
      );
    },
  },
];
