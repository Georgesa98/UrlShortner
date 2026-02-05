"use client";

import { Controller, useForm } from "react-hook-form";
import * as z from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Switch } from "@/components/ui/switch";
import { toast } from "sonner";
import { systemConfigSchema, SystemConfigFormData } from "./schema";
import { updateSystemConfigsAction, SystemConfig } from "./server";
import { Shield, Link2, BarChart3 } from "lucide-react";

interface SystemConfigClientProps {
  configs: SystemConfig[];
}

export default function SystemConfigClient({
  configs,
}: SystemConfigClientProps) {
  // Convert configs array to object for form default values
  const configsMap = configs.reduce((acc, config) => {
    acc[config.key] = config.value;
    return acc;
  }, {} as Record<string, string>);

  // Parse values to correct types for form
  const defaultValues: SystemConfigFormData = {
    rate_limit_ip: configsMap.rate_limit_ip || "100/hour",
    rate_limit_user: configsMap.rate_limit_user || "1000/hour",
    jwt_access_token_minutes: parseInt(
      configsMap.jwt_access_token_minutes || "5"
    ),
    short_code_length: parseInt(configsMap.short_code_length || "8"),
    short_code_pool_size: parseInt(configsMap.short_code_pool_size || "10000"),
    analytics_track_ip:
      configsMap.analytics_track_ip?.toLowerCase() === "true" || true,
    max_urls_per_user: parseInt(configsMap.max_urls_per_user || "100"),
    url_mapping_cache_timeout: parseInt(
      configsMap.url_mapping_cache_timeout || "3600"
    ),
  };

  const form = useForm<SystemConfigFormData>({
    resolver: zodResolver(systemConfigSchema),
    defaultValues,
  });

  const handleSubmit = async (data: SystemConfigFormData) => {
    try {
      const result = await updateSystemConfigsAction(data);

      if (result.success) {
        toast.success(result.message || "Configuration updated successfully");
        form.reset(data); // Reset form with new values as defaults
      } else {
        if (result.errors) {
          // Handle field-specific errors from backend
          Object.entries(result.errors).forEach(([key, errors]) => {
            if (key in data) {
              form.setError(key as keyof SystemConfigFormData, {
                type: "server",
                message: Array.isArray(errors) ? errors.join(", ") : String(errors),
              });
            }
          });
        }
        toast.error(result.message || "Failed to update configuration");
      }
    } catch {
      toast.error("An unexpected error occurred");
    }
  };

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h1 className="font-black text-2xl">System Configuration</h1>
        <p className="text-muted-foreground text-sm">
          Manage core system settings and behavior
        </p>
      </div>

      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
        {/* Security & Rate Limiting Section */}
        <Card className="bg-surface border-none">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-brand-blue" />
              <CardTitle className="text-text-main">
                Security & Rate Limiting
              </CardTitle>
            </div>
            <CardDescription>
              Protect the service from abuse
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Controller
              control={form.control}
              name="rate_limit_ip"
              render={({ field, fieldState }) => (
                <Field>
                  <FieldLabel htmlFor={field.name}>
                    Max Requests Per Minute (IP)
                  </FieldLabel>
                  <p className="text-xs text-muted-foreground mb-2">
                    Rate limit per IP address (e.g., 120/minute, 100/hour)
                  </p>
                  <Input
                    {...field}
                    id={field.name}
                    aria-invalid={fieldState.invalid}
                    placeholder="100/hour"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />

            <Controller
              control={form.control}
              name="rate_limit_user"
              render={({ field, fieldState }) => (
                <Field>
                  <FieldLabel htmlFor={field.name}>
                    Max Requests Per Minute (User)
                  </FieldLabel>
                  <p className="text-xs text-muted-foreground mb-2">
                    Rate limit per authenticated user (e.g., 1000/hour)
                  </p>
                  <Input
                    {...field}
                    id={field.name}
                    aria-invalid={fieldState.invalid}
                    placeholder="1000/hour"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />

            <Controller
              control={form.control}
              name="jwt_access_token_minutes"
              render={({ field, fieldState }) => (
                <Field>
                  <FieldLabel htmlFor={field.name}>
                    JWT Access Token Lifetime (minutes)
                  </FieldLabel>
                  <p className="text-xs text-muted-foreground mb-2">
                    How long JWT access tokens remain valid
                  </p>
                  <Input
                    {...field}
                    id={field.name}
                    type="number"
                    min="1"
                    aria-invalid={fieldState.invalid}
                    placeholder="5"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
          </CardContent>
        </Card>

        {/* Shortening Logic Section */}
        <Card className="bg-surface border-none">
          <CardHeader>
            <div className="flex items-center gap-2">
              <Link2 className="h-5 w-5 text-brand-blue" />
              <CardTitle className="text-text-main">Shortening Logic</CardTitle>
            </div>
            <CardDescription>
              Rules defining how short codes are generated
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Controller
              control={form.control}
              name="short_code_length"
              render={({ field, fieldState }) => (
                <Field>
                  <FieldLabel htmlFor={field.name}>
                    Minimum Hash Length
                  </FieldLabel>
                  <p className="text-xs text-muted-foreground mb-2">
                    Character length for generated short codes (4-128)
                  </p>
                  <Input
                    {...field}
                    id={field.name}
                    type="number"
                    min="4"
                    max="128"
                    aria-invalid={fieldState.invalid}
                    placeholder="8"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />

            <Controller
              control={form.control}
              name="short_code_pool_size"
              render={({ field, fieldState }) => (
                <Field>
                  <FieldLabel htmlFor={field.name}>
                    Short Code Pool Size
                  </FieldLabel>
                  <p className="text-xs text-muted-foreground mb-2">
                    Number of pre-generated short codes to maintain
                  </p>
                  <Input
                    {...field}
                    id={field.name}
                    type="number"
                    min="1"
                    aria-invalid={fieldState.invalid}
                    placeholder="10000"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
          </CardContent>
        </Card>

        {/* Analytics & Limits Section */}
        <Card className="bg-surface border-none">
          <CardHeader>
            <div className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-brand-blue" />
              <CardTitle className="text-text-main">
                Analytics & Limits
              </CardTitle>
            </div>
            <CardDescription>
              User limits and tracking preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <Controller
              control={form.control}
              name="analytics_track_ip"
              render={({ field }) => (
                <Field>
                  <div className="flex items-center justify-between">
                    <div className="space-y-1">
                      <FieldLabel htmlFor={field.name}>
                        Enable IP Tracking
                      </FieldLabel>
                      <p className="text-xs text-muted-foreground">
                        Track IP addresses in analytics for visitor insights
                      </p>
                    </div>
                    <Switch
                      id={field.name}
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </div>
                </Field>
              )}
            />

            <Controller
              control={form.control}
              name="max_urls_per_user"
              render={({ field, fieldState }) => (
                <Field>
                  <FieldLabel htmlFor={field.name}>
                    Max URLs Per User
                  </FieldLabel>
                  <p className="text-xs text-muted-foreground mb-2">
                    Maximum number of shortened URLs each user can create
                  </p>
                  <Input
                    {...field}
                    id={field.name}
                    type="number"
                    min="1"
                    aria-invalid={fieldState.invalid}
                    placeholder="100"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />

            <Controller
              control={form.control}
              name="url_mapping_cache_timeout"
              render={({ field, fieldState }) => (
                <Field>
                  <FieldLabel htmlFor={field.name}>
                    Cache Timeout (seconds)
                  </FieldLabel>
                  <p className="text-xs text-muted-foreground mb-2">
                    How long URL mappings are cached in memory
                  </p>
                  <Input
                    {...field}
                    id={field.name}
                    type="number"
                    min="0"
                    aria-invalid={fieldState.invalid}
                    placeholder="3600"
                  />
                  {fieldState.invalid && (
                    <FieldError errors={[fieldState.error]} />
                  )}
                </Field>
              )}
            />
          </CardContent>
        </Card>

        {/* Save Button */}
        <div className="flex justify-end">
          <Button
            type="submit"
            disabled={form.formState.isSubmitting}
            className="min-w-[120px]"
          >
            {form.formState.isSubmitting ? "Saving..." : "Save Changes"}
          </Button>
        </div>
      </form>
    </div>
  );
}
