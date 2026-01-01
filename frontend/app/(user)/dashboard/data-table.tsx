"use client";
import {
    ColumnDef,
    flexRender,
    getCoreRowModel,
    useReactTable,
} from "@tanstack/react-table";

interface DataTableProps<TData, TValue> {
    columns: ColumnDef<TData, TValue>[];
    data: TData[];
}
export function DataTable<TData, TValue>({
    columns,
    data,
}: DataTableProps<TData, TValue>) {
    const table = useReactTable({
        data,
        columns,
        getCoreRowModel: getCoreRowModel(),
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
            <div className="mt-4 flex items-center justify-between px-2 text-sm text-slate-500">
                <span>Showing 1-3 of 45 links</span>
                <div className="flex gap-2">
                    <button className="rounded bg-slate-800 px-3 py-1 disabled:opacity-50">
                        Previous
                    </button>
                    <button className="rounded bg-slate-800 px-3 py-1 text-white">
                        Next
                    </button>
                </div>
            </div>
        </div>
    );
}
