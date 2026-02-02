"use server";
import UserDashboard from "./client";
import { fetchTopVisitedUrlsAction, getUserStatsAction } from "./server";

export default async function Page() {
  const { data: userStats } = await getUserStatsAction({ days: 7 });
  const { data: topVisitedUrls } = await fetchTopVisitedUrlsAction();
  return (
    <UserDashboard userStats={userStats} topVisitedUrls={topVisitedUrls} />
  );
}
