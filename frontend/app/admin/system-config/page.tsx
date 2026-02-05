"use server";

import SystemConfigClient from "./client";
import { getSystemConfigsAction } from "./server";
import { redirect } from "next/navigation";

export default async function SystemConfigPage() {
  const { success, data } = await getSystemConfigsAction();

  if (!success || !data) {
    redirect("/admin/dashboard");
  }

  return <SystemConfigClient configs={data} />;
}
