"use server";
import UserManagementClient from "./client";
import { fetchUsersAction, getUsersData } from "./server";

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
    const { success, status, data } = await fetchUsersAction({
        page: parseInt(page),
        limit: parseInt(limit),
        query: query,
    });
    return (
        <UserManagementClient
            users={data.data.users}
            pagination={data.data.pagination}
        />
    );
}
