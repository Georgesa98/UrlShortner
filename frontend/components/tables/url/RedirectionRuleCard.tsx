"use client";

import * as React from "react";
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
  DEVICE_TYPES,
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

export function RedirectionRuleCard({
  rule,
  ruleNumber,
  isExpanded,
  onSave,
  onDiscard,
}: RedirectionRuleCardProps) {
  const [formData, setFormData] = React.useState<RedirectionRule>(
    rule || {
      name: "",
      target_url: "",
      priority: ruleNumber || 1,
      is_active: true,
      conditions: {},
    },
  );

  const updateField = (field: keyof RedirectionRule, value: any) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const updateCondition = (field: string, value: any) => {
    setFormData((prev) => ({
      ...prev,
      conditions: { ...prev.conditions, [field]: value },
    }));
  };

  const handleSave = () => {
    if (formData.name && formData.target_url) {
      onSave(formData);
    }
  };

  const getConditionSummary = () => {
    const parts: string[] = [];
    if (formData.conditions.country?.length) {
      parts.push(formData.conditions.country.join(", "));
    }
    if (formData.conditions.device_type?.length) {
      parts.push(formData.conditions.device_type.join(", "));
    }
    return parts.length > 0 ? parts.join(" | ") : "No conditions";
  };

  const countryOptions: MultiInputOption[] = COUNTRIES.map((c) => ({
    value: c.code,
    label: c.name,
    icon: c.flag,
  }));

  if (!isExpanded && rule) {
    // Collapsed view
    return (
      <div className="flex items-center justify-between p-4 rounded-lg bg-surface border border-border">
        <div className="flex items-center gap-4 flex-1">
          <span className="text-xs font-mono text-muted-foreground">
            #{ruleNumber}
          </span>
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <h4 className="font-bold text-sm">{rule.name}</h4>
              <Badge
                variant={rule.is_active ? "success" : "secondary"}
                className="uppercase text-xs"
              >
                {rule.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground">
              {getConditionSummary()}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-sm text-muted-foreground">
            → {rule.target_url}
          </span>
          <span className="text-sm font-mono text-muted-foreground">
            Priority: {rule.priority}
          </span>
        </div>
      </div>
    );
  }

  // Expanded form view
  return (
    <div className="p-6 rounded-lg bg-surface border border-border space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <Field>
            <FieldLabel className="font-bold text-sm">Rule Name</FieldLabel>
            <Input
              value={formData.name}
              onChange={(e) => updateField("name", e.target.value)}
              placeholder="e.g., Android Fallback Rule"
              className="bg-background"
            />
          </Field>
        </div>
        <div className="flex items-center gap-4 ml-4">
          <Field>
            <FieldLabel className="font-bold text-sm">Priority</FieldLabel>
            <Input
              type="number"
              value={formData.priority}
              onChange={(e) =>
                updateField("priority", parseInt(e.target.value) || 0)
              }
              className="w-20 bg-background"
            />
          </Field>
          <div className="flex items-center gap-2 pt-6">
            <Switch
              checked={formData.is_active}
              onCheckedChange={(checked) => updateField("is_active", checked)}
            />
            <span className="text-sm font-medium">
              {formData.is_active ? "Active" : "Inactive"}
            </span>
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
        <Input
          value={formData.target_url}
          onChange={(e) => updateField("target_url", e.target.value)}
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
            <MultiInput
              options={countryOptions}
              selected={formData.conditions.country || []}
              onChange={(selected) => updateCondition("country", selected)}
              placeholder="Add countries..."
              emptyText="No countries found"
            />
          </Field>

          {/* Device Types */}
          <Field>
            <FieldLabel className="font-bold text-sm">Device Types</FieldLabel>
            <ToggleGroup
              type="multiple"
              value={formData.conditions.device_type || []}
              onValueChange={(value) => updateCondition("device_type", value)}
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
          </Field>

          {/* Operating System */}
          <Field>
            <FieldLabel className="font-bold text-sm">
              Operating System
            </FieldLabel>
            <MultiSelectList
              options={OPERATING_SYSTEMS}
              selected={formData.conditions.os || []}
              onChange={(selected) => updateCondition("os", selected)}
            />
            <p className="text-xs text-muted-foreground mt-1">
              Hold Cmd/Ctrl to select multiple
            </p>
          </Field>

          {/* Browser */}
          <Field>
            <FieldLabel className="font-bold text-sm">Browser</FieldLabel>
            <MultiSelectList
              options={BROWSERS}
              selected={formData.conditions.browser || []}
              onChange={(selected) => updateCondition("browser", selected)}
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
            <Input
              value={formData.conditions.referer || ""}
              onChange={(e) => updateCondition("referer", e.target.value)}
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
              <TimePicker
                value={formData.conditions.time_range?.start || ""}
                onChange={(value) =>
                  updateCondition("time_range", {
                    ...formData.conditions.time_range,
                    start: value,
                  })
                }
                placeholder="--:--"
              />
              <span className="text-sm text-muted-foreground">to</span>
              <TimePicker
                value={formData.conditions.time_range?.end || ""}
                onChange={(value) =>
                  updateCondition("time_range", {
                    ...formData.conditions.time_range,
                    end: value,
                  })
                }
                placeholder="--:--"
              />
            </div>
          </Field>
        </div>
      </div>

      <Separator />

      {/* Actions */}
      <div className="flex justify-end gap-2">
        <Button variant="ghost" onClick={onDiscard}>
          Discard Changes
        </Button>
        <Button
          onClick={handleSave}
          disabled={!formData.name || !formData.target_url}
        >
          Save Rule
        </Button>
      </div>
    </div>
  );
}
