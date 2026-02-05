"use server";
import SettingsClient from "@/app/(user)/settings/client";
import { getUserProfileAction } from "@/app/(user)/settings/server";

export default async function AdminSettingsPage() {
  const { data: userProfile } = await getUserProfileAction();

  return <SettingsClient userProfile={userProfile} />;
}
