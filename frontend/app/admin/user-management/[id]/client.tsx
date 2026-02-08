"use client";

import { ListUrlsResponse, UrlResponse, UserResponse } from "@/api-types";
import { adminUrlColumns } from "@/components/tables/admin-url/columns";
import { AdminUrlDataTable } from "@/components/tables/admin-url/data-table";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

export default function UserUrlClient({
  urls,
  user,
}: {
  urls: ListUrlsResponse;
  user: UserResponse;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParam = useSearchParams();

  function handlePageChange(newPage: number) {
    const params = new URLSearchParams(searchParam.toString());
    params.set("page", newPage.toString());
    router.push(`${pathname}?${params.toString()}`, { scroll: false });
    router.refresh();
  }
  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold">
        {user?.first_name} {user?.last_name} URLs:
      </h1>
      <AdminUrlDataTable
        columns={adminUrlColumns}
        data={urls.urls}
        pagination={urls.pagination}
        onPageChange={handlePageChange}
      />
    </div>
  );
}
