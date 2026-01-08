"use client";
import { Pagination } from "@/api-types";
import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    useReactTable,
} from "@tanstack/react-table";
import { useMemo } from "react";

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    pagination: Pagination;
    onPageChange?: (page: number) => void;
    control: boolean;
}
export function UrlDataTable<TData, TValue>({
    columns,
    data,
    pagination,
    onPageChange,
    control,
}: DataTableProps<TData, TValue>) {
    const tablePagination = useMemo(
        () => ({
            pageIndex: pagination.page - 1,
            pageSize: pagination.limit,
        }),
        [pagination]
    );
    const table = useReactTable({
        data,
        columns,
        pageCount: pagination.total_pages,
        state: {
            pagination: tablePagination,
        },
        onPaginationChange: (updater) => {
            if (typeof updater === "function") {
                const newState = updater(tablePagination);
                onPageChange?.(newState.pageIndex + 1);
            }
        },
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
    });

    return (
        <div className="rounded-xl border border-slate-800 bg-[#0f172a] p-4">
            <table className="w-full text-left border-separate border-spacing-y-4">
                <thead>
                    {table.getHeaderGroups().map((headerGroup) => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                                <th
                                    key={header.id}
                                    className="pb-2 pl-4 text-xs font-semibold text-slate-500 uppercase tracking-wider"
                                >
                                    {flexRender(
                                        header.column.columnDef.header,
                                        header.getContext()
                                    )}
                                </th>
                            ))}
                        </tr>
                    ))}
                </thead>
                <tbody>
                    {table.getRowModel().rows.map((row) => (
                        <tr
                            key={row.id}
                            className="group bg-[#1e293b]/30 hover:bg-[#1e293b]/50 transition-colors"
                        >
                            {row.getVisibleCells().map((cell) => (
                                <td
                                    key={cell.id}
                                    className="py-3 pl-4 first:rounded-l-lg last:rounded-r-lg"
                                >
                                    {flexRender(
                                        cell.column.columnDef.cell,
                                        cell.getContext()
                                    )}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* Footer / Pagination */}
            {control && (
                <div className="mt-4 flex items-center justify-between px-2 text-sm text-slate-500">
                    <span>
                        Showing {data.length} of {pagination.total} links
                    </span>
                    <div className="flex gap-2">
                        <button
                            onClick={() => {
                                table.previousPage();
                            }}
                            disabled={!pagination.has_previous}
                            className="rounded bg-slate-800 px-3 py-1 text-white disabled:text-muted-foreground disabled:opacity-50"
                        >
                            Previous
                        </button>
                        <button
                            onClick={() => {
                                table.nextPage();
                            }}
                            disabled={!pagination.has_next}
                            className="rounded bg-slate-800 px-3 py-1 text-white disabled:text-muted-foreground  disabled:opacity-50"
                        >
                            Next
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
