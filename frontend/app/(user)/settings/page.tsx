"use server";
import SettingsClient from "./client";
import { getUserProfileAction } from "./server";

export default async function Page() {
  const { data: userProfile } = await getUserProfileAction();
  console.log(userProfile);

  return <SettingsClient userProfile={userProfile} />;
}
