"use server";
import UserManagementClient from "./client";
import { fetchUsersAction } from "./server";

export default async function Page({
    searchParams,
}: {
    searchParams: Promise<{
        [key: string]: string | string[] | undefined;
    }>;
}) {
    const params = await searchParams;
    const page = (params.page as string) || "1";
    const limit = (params.limit as string) || "10";
    const query = (params.query as string) || "";
    const roles = (params.roles as string) || "";
    const is_active = (params.is_active as string) || "";
    const order_by = (params.order_by as string) || "-date_joined";
    const { success, status, data } = await fetchUsersAction({
        page: parseInt(page),
        limit: parseInt(limit),
        query: query,
        roles: roles,
        is_active: is_active,
        order_by: order_by,
    });
    return (
        <UserManagementClient
            users={data.data.users}
            pagination={data.data.pagination}
        />
    );
}
