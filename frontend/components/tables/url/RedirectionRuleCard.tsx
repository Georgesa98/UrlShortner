"use client";

import * as React from "react";
import { useForm, Controller, Control, useWatch } from "react-hook-form";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Field, FieldLabel } from "@/components/ui/field";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { MultiInput, MultiInputOption } from "@/components/ui/multi-input";
import { MultiSelectList } from "@/components/ui/multi-select-list";
import { TimePicker } from "@/components/ui/time-picker";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import {
  COUNTRIES,
  OPERATING_SYSTEMS,
  BROWSERS,
} from "@/lib/constants/redirection";
import { Monitor, Smartphone, Tablet } from "lucide-react";

export interface RedirectionRule {
  id?: string;
  name: string;
  target_url: string;
  priority: number;
  is_active: boolean;
  conditions: {
    country?: string[];
    device_type?: string[];
    os?: string[];
    browser?: string[];
    referer?: string;
    time_range?: {
      start: string;
      end: string;
    };
  };
}

interface RedirectionRuleCardProps {
  rule?: RedirectionRule;
  ruleNumber?: number;
  isExpanded: boolean;
  onSave: (rule: RedirectionRule) => void;
  onDiscard: () => void;
}

// PERFORMANCE: Move expensive country mapping outside component to prevent re-creation on every render
const countryOptions: MultiInputOption[] = COUNTRIES.map((c) => ({
  value: c.code,
  label: c.name,
  icon: c.flag,
}));

// PERFORMANCE: Isolated component for collapsed view - only re-renders when its watched values change
const CollapsedRuleView = React.memo(function CollapsedRuleView({
  control,
  ruleNumber,
}: {
  control: Control<RedirectionRule>;
  ruleNumber?: number;
}) {
  const values = useWatch({ control });

  const conditionSummary = React.useMemo(() => {
    const parts: string[] = [];
    if (values.conditions?.country?.length) {
      parts.push(values.conditions.country.join(", "));
    }
    if (values.conditions?.device_type?.length) {
      parts.push(values.conditions.device_type.join(", "));
    }
    return parts.length > 0 ? parts.join(" | ") : "No conditions";
  }, [values.conditions?.country, values.conditions?.device_type]);

  return (
    <div className="flex items-center justify-between p-4 rounded-lg bg-surface border border-border">
      <div className="flex items-center gap-4 flex-1">
        <span className="text-xs font-mono text-muted-foreground">
          #{ruleNumber}
        </span>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <h4 className="font-bold text-sm">{values.name}</h4>
            <Badge
              variant={values.is_active ? "success" : "secondary"}
              className="uppercase text-xs"
            >
              {values.is_active ? "Active" : "Inactive"}
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground">{conditionSummary}</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <span className="text-sm text-muted-foreground">
          → {values.target_url}
        </span>
        <span className="text-sm font-mono text-muted-foreground">
          Priority: {values.priority}
        </span>
      </div>
    </div>
  );
});

// PERFORMANCE: Isolated component for Active/Inactive label - only re-renders when is_active changes
const ActiveStatusLabel = React.memo(function ActiveStatusLabel({
  control,
}: {
  control: Control<RedirectionRule>;
}) {
  const isActive = useWatch({ control, name: "is_active" });
  return (
    <span className="text-sm font-medium">
      {isActive ? "Active" : "Inactive"}
    </span>
  );
});

// PERFORMANCE: Isolated component for Save button footer - only re-renders when name/target_url change
const SaveButtonFooter = React.memo(function SaveButtonFooter({
  control,
  onDiscard,
  onSubmit,
}: {
  control: Control<RedirectionRule>;
  onDiscard: () => void;
  onSubmit: () => void;
}) {
  const [name, targetUrl] = useWatch({
    control,
    name: ["name", "target_url"],
  });

  return (
    <div className="flex justify-end gap-2">
      <Button variant="ghost" onClick={onDiscard}>
        Discard Changes
      </Button>
      <Button onClick={onSubmit} disabled={!name || !targetUrl}>
        Save Rule
      </Button>
    </div>
  );
});

function RedirectionRuleCardComponent({
  rule,
  ruleNumber,
  isExpanded,
  onSave,
  onDiscard,
}: RedirectionRuleCardProps) {
  // PERFORMANCE: Use react-hook-form with register() for uncontrolled inputs (zero re-renders on typing)
  const { control, handleSubmit, register } = useForm<RedirectionRule>({
    defaultValues: rule || {
      name: "",
      target_url: "",
      priority: ruleNumber || 1,
      is_active: true,
      conditions: {},
    },
  });

  // Submit handler
  const onSubmit = React.useCallback(() => {
    handleSubmit((data) => {
      onSave(data);
    })();
  }, [handleSubmit, onSave]);

  // PERFORMANCE: Collapsed view is isolated - main component doesn't re-render when form values change
  if (!isExpanded && rule) {
    return <CollapsedRuleView control={control} ruleNumber={ruleNumber} />;
  }

  // Expanded form view
  return (
    <div className="p-6 rounded-lg bg-surface border border-border space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <Field>
            <FieldLabel className="font-bold text-sm">Rule Name</FieldLabel>
            {/* PERFORMANCE: Using register() instead of Controller for zero re-renders on typing */}
            <Input
              {...register("name")}
              placeholder="e.g., Android Fallback Rule"
              className="bg-background"
            />
          </Field>
        </div>
        <div className="flex items-center gap-4 ml-4">
          <Field>
            <FieldLabel className="font-bold text-sm">Priority</FieldLabel>
            <Input
              {...register("priority", { valueAsNumber: true })}
              type="number"
              className="w-20 bg-background"
            />
          </Field>
          <div className="flex items-center gap-2 pt-6">
            <Controller
              name="is_active"
              control={control}
              render={({ field }) => (
                <Switch
                  checked={field.value}
                  onCheckedChange={field.onChange}
                />
              )}
            />
            {/* PERFORMANCE: Isolated component for the label */}
            <ActiveStatusLabel control={control} />
          </div>
        </div>
      </div>

      <Separator />

      {/* Redirect To */}
      <Field>
        <FieldLabel className="font-bold text-sm flex items-center gap-2">
          <span className="text-primary">→</span>
          Redirect To
        </FieldLabel>
        {/* PERFORMANCE: Using register() instead of Controller for zero re-renders on typing */}
        <Input
          {...register("target_url")}
          placeholder="https://play.google.com/store/apps/details?id=com.shortnr.app"
          className="bg-background"
        />
      </Field>

      <Separator />

      {/* Targeting Conditions */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          Targeting Conditions
        </h3>

        <div className="grid grid-cols-2 gap-4">
          {/* Countries */}
          <Field>
            <FieldLabel className="font-bold text-sm">
              Countries (ISO)
            </FieldLabel>
            <Controller
              name="conditions.country"
              control={control}
              render={({ field }) => (
                <MultiInput
                  options={countryOptions}
                  selected={field.value || []}
                  onChange={field.onChange}
                  placeholder="Add countries..."
                  emptyText="No countries found"
                />
              )}
            />
          </Field>

          {/* Device Types */}
          <Field>
            <FieldLabel className="font-bold text-sm">Device Types</FieldLabel>
            <Controller
              name="conditions.device_type"
              control={control}
              render={({ field }) => (
                <ToggleGroup
                  type="multiple"
                  value={field.value || []}
                  onValueChange={field.onChange}
                  className="justify-start gap-2"
                >
                  <ToggleGroupItem
                    value="mobile"
                    aria-label="Mobile"
                    className="flex items-center gap-2 px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
                  >
                    <Smartphone size={16} />
                    Mobile
                  </ToggleGroupItem>
                  <ToggleGroupItem
                    value="desktop"
                    aria-label="Desktop"
                    className="flex items-center gap-2 px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
                  >
                    <Monitor size={16} />
                    Desktop
                  </ToggleGroupItem>
                  <ToggleGroupItem
                    value="tablet"
                    aria-label="Tablet"
                    className="flex items-center gap-2 px-4 data-[state=on]:bg-primary data-[state=on]:text-primary-foreground"
                  >
                    <Tablet size={16} />
                    Tablet
                  </ToggleGroupItem>
                </ToggleGroup>
              )}
            />
          </Field>

          {/* Operating System */}
          <Field>
            <FieldLabel className="font-bold text-sm">
              Operating System
            </FieldLabel>
            <Controller
              name="conditions.os"
              control={control}
              render={({ field }) => (
                <MultiSelectList
                  options={OPERATING_SYSTEMS}
                  selected={field.value || []}
                  onChange={field.onChange}
                />
              )}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Hold Cmd/Ctrl to select multiple
            </p>
          </Field>

          {/* Browser */}
          <Field>
            <FieldLabel className="font-bold text-sm">Browser</FieldLabel>
            <Controller
              name="conditions.browser"
              control={control}
              render={({ field }) => (
                <MultiSelectList
                  options={BROWSERS}
                  selected={field.value || []}
                  onChange={field.onChange}
                />
              )}
            />
          </Field>
        </div>
      </div>

      <Separator />

      {/* Advanced Conditions */}
      <div className="space-y-4">
        <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
          Advanced Conditions
        </h3>

        <div className="grid grid-cols-2 gap-4">
          {/* Referrer URL Pattern */}
          <Field>
            <FieldLabel className="font-bold text-sm">
              Referrer URL Pattern
            </FieldLabel>
            {/* PERFORMANCE: Using register() instead of Controller for zero re-renders on typing */}
            <Input
              {...register("conditions.referer")}
              placeholder="e.g., *facebook.com*"
              className="bg-background"
            />
          </Field>

          {/* Time Range */}
          <Field>
            <FieldLabel className="font-bold text-sm">
              Time Range (UTC)
            </FieldLabel>
            <div className="flex items-center gap-2">
              <Controller
                name="conditions.time_range.start"
                control={control}
                render={({ field }) => (
                  <TimePicker
                    value={field.value || ""}
                    onChange={field.onChange}
                    placeholder="--:--"
                  />
                )}
              />
              <span className="text-sm text-muted-foreground">to</span>
              <Controller
                name="conditions.time_range.end"
                control={control}
                render={({ field }) => (
                  <TimePicker
                    value={field.value || ""}
                    onChange={field.onChange}
                    placeholder="--:--"
                  />
                )}
              />
            </div>
          </Field>
        </div>
      </div>

      <Separator />

      {/* PERFORMANCE: Isolated footer component - only re-renders when name/target_url change */}
      <SaveButtonFooter
        control={control}
        onDiscard={onDiscard}
        onSubmit={onSubmit}
      />
    </div>
  );
}

// PERFORMANCE: Memoize component to prevent unnecessary re-renders from parent
export const RedirectionRuleCard = React.memo(
  RedirectionRuleCardComponent,
  (prevProps, nextProps) => {
    // Only re-render if relevant props change
    if (prevProps.isExpanded !== nextProps.isExpanded) return false;
    if (prevProps.ruleNumber !== nextProps.ruleNumber) return false;

    // If both have no rule, they're equal
    if (!prevProps.rule && !nextProps.rule) return true;

    // If one has rule and other doesn't, they're different
    if (!prevProps.rule || !nextProps.rule) return false;

    // Compare rule properties
    return (
      prevProps.rule.id === nextProps.rule.id &&
      prevProps.rule.name === nextProps.rule.name &&
      prevProps.rule.target_url === nextProps.rule.target_url &&
      prevProps.rule.priority === nextProps.rule.priority &&
      prevProps.rule.is_active === nextProps.rule.is_active
    );
  }
);
