"use client";
import { Pagination } from "@/api-types";
import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    useReactTable,
    RowSelectionState,
} from "@tanstack/react-table";
import { useMemo } from "react";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

interface UserManagementDataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
    pagination: Pagination;
    onPageChange?: (page: number) => void;
    onRowClick?: (data: TData) => void;
    rowSelection: RowSelectionState;
    onRowSelectionChange: (selection: RowSelectionState) => void;
}

export function UserManagementDataTable<TData, TValue>({
    columns,
    data,
    pagination,
    onPageChange,
    onRowClick,
    rowSelection,
    onRowSelectionChange,
}: UserManagementDataTableProps<TData, TValue>) {
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
            rowSelection,
        },
        onRowSelectionChange,
        onPaginationChange: (updater) => {
            if (typeof updater === "function") {
                const newState = updater(tablePagination);
                onPageChange?.(newState.pageIndex + 1);
            }
        },
        getCoreRowModel: getCoreRowModel(),
        manualPagination: true,
        enableRowSelection: true,
    });

    return (
        <div className="bg-surface rounded-xl overflow-hidden">
            <Table>
                <TableHeader>
                    {table.getHeaderGroups().map((headerGroup) => (
                        <tr key={headerGroup.id}>
                            {headerGroup.headers.map((header) => (
                                <TableHead
                                    key={header.id}
                                    className="text-text-muted font-medium uppercase text-xs tracking-wider"
                                >
                                    {header.isPlaceholder
                                        ? null
                                        : flexRender(
                                              header.column.columnDef.header,
                                              header.getContext()
                                          )}
                                </TableHead>
                            ))}
                        </tr>
                    ))}
                </TableHeader>
                <TableBody>
                    {table.getRowModel().rows.length === 0 ? (
                        <TableRow>
                            <TableCell
                                colSpan={columns.length}
                                className="text-center py-10 text-text-muted"
                            >
                                No users found
                            </TableCell>
                        </TableRow>
                    ) : (
                        table.getRowModel().rows.map((row) => (
                            <TableRow
                                key={row.id}
                                onClick={() => onRowClick?.(row.original)}
                                className={`border-border-subtle hover:bg-surface-hover transition-colors ${
                                    onRowClick ? "cursor-pointer" : ""
                                }`}
                            >
                                {row.getVisibleCells().map((cell) => (
                                    <TableCell key={cell.id}>
                                        {flexRender(
                                            cell.column.columnDef.cell,
                                            cell.getContext()
                                        )}
                                    </TableCell>
                                ))}
                            </TableRow>
                        ))
                    )}
                </TableBody>
            </Table>

            {data.length > 0 && (
                <div className="flex items-center justify-between bg-surface p-4 border-t border-border-subtle">
                    <p className="text-sm text-text-muted">
                        Showing {(pagination.page - 1) * pagination.limit + 1}{" "}
                        to{" "}
                        {Math.min(
                            pagination.page * pagination.limit,
                            pagination.total
                        )}{" "}
                        of {pagination.total} URLs
                    </p>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => table.previousPage()}
                            disabled={!pagination.has_previous}
                            className="px-4 py-2 bg-surface-hover rounded-lg text-text-main disabled:opacity-50 hover:bg-accent transition-colors text-sm font-medium"
                        >
                            Previous
                        </button>
                        <button
                            onClick={() => table.nextPage()}
                            disabled={!pagination.has_next}
                            className="px-4 py-2 bg-surface-hover rounded-lg text-text-main disabled:opacity-50 hover:bg-accent transition-colors text-sm font-medium"
                        >
                            Next
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
