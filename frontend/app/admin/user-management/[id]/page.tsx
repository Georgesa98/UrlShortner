"use server";
import { getUserDetailsAction, getUserUrlsAction } from "../server";
import UserUrlClient from "./client";

export default async function Page({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ page: string }>;
}) {
  const { id } = await params;
  const { page } = await searchParams;
  const { data: user } = await getUserDetailsAction({
    user_id: id,
  });

  const { data: urls } = await getUserUrlsAction({
    user_id: id,
    page: parseInt(page),
    limit: 10,
  });
  console.log(urls);
  return <UserUrlClient urls={urls} user={user} />;
}
