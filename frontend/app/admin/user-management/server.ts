"use server";
import { GetUsersListResponse, UserResponse, Pagination } from "@/api-types";
import axiosInstance from "@/app/api/axiosInstance";
import { AxiosError } from "axios";

export async function getUsersData(
    page: number = 1,
    limit: number = 10
): Promise<{ users: UserResponse[]; pagination: Pagination }> {
    const mockUsers: UserResponse[] = [
        {
            id: 1,
            username: "sarah_c84",
            email: "sarah.c@example.com",
            first_name: "Sarah",
            last_name: "Connor",
            role: "ADMIN",
            is_active: true,
            date_joined: "2022-10-24T00:00:00Z",
            last_login: "2024-01-20T10:30:00Z",
        },
        {
            id: 2,
            username: "mike_foster",
            email: "mike.foster@example.com",
            first_name: "Michael",
            last_name: "Foster",
            role: "USER",
            is_active: false,
            date_joined: "2023-03-15T00:00:00Z",
            last_login: "2024-01-15T14:22:00Z",
        },
        {
            id: 3,
            username: "dries_v",
            email: "dries.vincent@example.com",
            first_name: "Dries",
            last_name: "Vincent",
            role: "STAFF",
            is_active: true,
            date_joined: "2023-06-10T00:00:00Z",
            last_login: "2024-01-19T09:15:00Z",
        },
        {
            id: 4,
            username: "john_doe",
            email: "john.doe@example.com",
            first_name: "John",
            last_name: "Doe",
            role: "USER",
            is_active: true,
            date_joined: "2023-08-22T00:00:00Z",
            last_login: "2024-01-18T16:45:00Z",
        },
        {
            id: 5,
            username: "jane_smith",
            email: "jane.smith@example.com",
            first_name: "Jane",
            last_name: "Smith",
            role: "USER",
            is_active: true,
            date_joined: "2023-09-05T00:00:00Z",
            last_login: "2024-01-17T11:20:00Z",
        },
        {
            id: 6,
            username: "alex_johnson",
            email: "alex.j@example.com",
            first_name: "Alex",
            last_name: "Johnson",
            role: "STAFF",
            is_active: true,
            date_joined: "2023-10-12T00:00:00Z",
            last_login: "2024-01-16T13:30:00Z",
        },
        {
            id: 7,
            username: "emily_brown",
            email: "emily.b@example.com",
            first_name: "Emily",
            last_name: "Brown",
            role: "USER",
            is_active: false,
            date_joined: "2023-11-08T00:00:00Z",
            last_login: "2024-01-10T08:00:00Z",
        },
        {
            id: 8,
            username: "david_lee",
            email: "david.lee@example.com",
            first_name: "David",
            last_name: "Lee",
            role: "USER",
            is_active: true,
            date_joined: "2023-12-01T00:00:00Z",
            last_login: "2024-01-19T15:10:00Z",
        },
        {
            id: 9,
            username: "sophia_wilson",
            email: "sophia.w@example.com",
            first_name: "Sophia",
            last_name: "Wilson",
            role: "USER",
            is_active: true,
            date_joined: "2024-01-03T00:00:00Z",
            last_login: "2024-01-18T12:25:00Z",
        },
        {
            id: 10,
            username: "james_taylor",
            email: "james.t@example.com",
            first_name: "James",
            last_name: "Taylor",
            role: "ADMIN",
            is_active: true,
            date_joined: "2024-01-10T00:00:00Z",
            last_login: "2024-01-20T09:00:00Z",
        },
    ];

    const mockPagination: Pagination = {
        total: 1240,
        page: page,
        limit: limit,
        total_pages: Math.ceil(1240 / limit),
        has_next: page < Math.ceil(1240 / limit),
        has_previous: page > 1,
    };

    return {
        users: mockUsers,
        pagination: mockPagination,
    };
}

export async function fetchUsersAction({
    page,
    limit,
    query,
}: {
    page: number;
    limit: number;
    query: string;
}) {
    try {
        const response = await axiosInstance.get(
            `/admin/user/?page=${page}&limit=${limit}&query=${query}`
        );
        return {
            success: true,
            status: response.status,
            data: response.data,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message: e.response?.data?.message || "Failed to fetch users",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
export async function bulkDeleteUsersAction({
    user_ids,
}: {
    user_ids: number[];
}) {
    try {
        const response = await axiosInstance.post("/admin/user/bulk-delete/", {
            user_ids,
        });
        return {
            success: true,
            status: response.status,
            message: response.data.message,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.message || "Failed to bulk delete users",
            };
        }

        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
export async function toggleBanUserAction({ user_id }: { user_id: number }) {
    try {
        const response = await axiosInstance.post(
            `/admin/user/${user_id}/ban/`
        );
        return {
            success: true,
            status: response.status,
            message: response.data.message,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message:
                    e.response?.data?.message || "Failed to toggle ban user",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
export async function getUserUrlsAction({ user_id }: { user_id: number }) {
    try {
        const response = await axiosInstance.get(
            `/admin/user/${user_id}/urls/`
        );
        return {
            success: true,
            status: response.status,
            data: response.data,
        };
    } catch (e: unknown) {
        if (e instanceof AxiosError) {
            return {
                success: false,
                status: e.response?.status || 500,
                message: e.response?.data?.message || "Failed to get user urls",
            };
        }
        return {
            success: false,
            status: 500,
            message: "An unexpected error occurred",
        };
    }
}
