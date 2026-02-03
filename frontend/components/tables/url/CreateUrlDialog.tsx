import {
  createBatchLinkFormSchema,
  createLinkFormSchema,
} from "@/app/(user)/urls/schema";
import {
  batchShortenUrlAction,
  createShortUrlAction,
} from "@/app/(user)/urls/server";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { DatePicker } from "@/components/ui/datePicker";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Field, FieldError, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import {
  RedirectionRuleCard,
  RedirectionRule,
} from "@/components/tables/url/RedirectionRuleCard";
import useHostname from "@/hooks/useHostname";
import { zodResolver } from "@hookform/resolvers/zod";
import { TabsContent, TabsList } from "@radix-ui/react-tabs";
import { Link, Plus, Settings, Layers, Zap, FlaskConical } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Controller, useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";

export default function CreateUrlDialog({
  buttonClassName,
}: {
  buttonClassName: string;
}) {
  const [activeTab, setActiveTab] = useState<string>("general");
  const [batchMode, setBatchMode] = useState<boolean>(false);
  const [rules, setRules] = useState<RedirectionRule[]>([]);
  const [showNewRuleForm, setShowNewRuleForm] = useState<boolean>(false);
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null);
  const hostname = useHostname();
  const router = useRouter();
  const batchUrlForm = useForm({
    resolver: zodResolver(createBatchLinkFormSchema),
    defaultValues: {
      urls: "",
    },
  });
  const singleUrlForm = useForm<z.infer<typeof createLinkFormSchema>>({
    resolver: zodResolver(createLinkFormSchema),
    defaultValues: {
      name: "",
      long_url: "",
      short_url: "",
      expiry_date: new Date(),
      password_protection: false,
      enable_tracking: true,
      redirection_rules: [],
    },
  });

  const handleSaveRule = (rule: RedirectionRule) => {
    const newRule = {
      ...rule,
      id: rule.id || `rule-${Date.now()}`,
    };
    setRules((prev) => {
      const existing = prev.findIndex((r) => r.id === newRule.id);
      if (existing >= 0) {
        const updated = [...prev];
        updated[existing] = newRule;
        return updated;
      }
      return [...prev, newRule];
    });
    setShowNewRuleForm(false);
    setEditingRuleId(null);
  };

  const handleDiscardRule = () => {
    setShowNewRuleForm(false);
    setEditingRuleId(null);
  };
  const onSubmitSingle = async (data: z.infer<typeof createLinkFormSchema>) => {
    const { message, status } = await createShortUrlAction({
      name: data.name || "",
      long_url: data.long_url,
      short_url: data.short_url || "",
      expiry_date: data.expiry_date?.toISOString() || "",
      redirection_rules: rules,
    });
    if (status === 201) {
      toast.success("Link created successfully");
      setTimeout(() => {
        router.refresh();
      }, 2000);
    } else {
      toast.error(message || "Failed to create link");
    }
  };
  const onSubmitBatch = async (
    data: z.infer<typeof createBatchLinkFormSchema>,
  ) => {
    const urlsToSubmit = data.urls.map((url) => ({
      name: url.name || "",
      long_url: url.long_url,
      short_url: url.short_url || "",
      expiry_date: url.expiry_date?.toISOString() || "",
    }));
    const { message, status } = await batchShortenUrlAction({
      data: urlsToSubmit,
    });
    if (status === 201) {
      toast.success("Batch links created successfully");
      setTimeout(() => {
        router.refresh();
      }, 2000);
    } else {
      toast.error(message || "Failed to create batch links");
    }
  };
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button className={buttonClassName}>
          <Plus />
          Create New
        </Button>
      </DialogTrigger>
      <DialogContent className="min-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
        <DialogHeader className="gap-1 shrink-0">
          <h1 className="text-2xl font-bold">Create New Link</h1>
          <p className="text-sm text-muted-foreground">
            Shorten your long URLs and customize your links.
          </p>
        </DialogHeader>
        <Tabs
          value={activeTab}
          onValueChange={setActiveTab}
          className="flex-1 flex flex-col min-h-0"
        >
          <TabsList className="grid w-full grid-cols-2 shrink-0">
            <TabsTrigger value="general" className="flex items-center gap-2">
              <Settings size={16} />
              General Settings
            </TabsTrigger>
            <TabsTrigger
              value="redirection"
              className="flex items-center gap-2"
            >
              <Layers size={16} />
              Redirection Rules
            </TabsTrigger>
          </TabsList>
          <TabsContent
            className="flex flex-col gap-4 overflow-y-auto flex-1 min-h-0"
            value="general"
          >
            <Separator className="w-full" />

            {/* Batch Mode Toggle */}
            <div className="flex items-center justify-between p-4 rounded-lg bg-surface border border-border">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-md bg-primary/10">
                  <Layers size={20} className="text-primary" />
                </div>
                <div>
                  <h3 className="font-bold text-sm">Batch Mode</h3>
                  <p className="text-sm text-muted-foreground">
                    Shorten multiple links at once
                  </p>
                </div>
              </div>
              <Switch checked={batchMode} onCheckedChange={setBatchMode} />
            </div>

            {!batchMode ? (
              <>
                {/* Single URL Form */}
                <Controller
                  name="long_url"
                  control={singleUrlForm.control}
                  render={({ field, fieldState }) => (
                    <Field>
                      <FieldLabel
                        htmlFor={field.name}
                        className="font-bold text-sm"
                      >
                        Destination URL
                      </FieldLabel>
                      <div className="relative">
                        <Input
                          {...field}
                          id={field.name}
                          aria-invalid={fieldState.invalid}
                          className="pl-10 h-12 text-sm bg-surface"
                          placeholder="https://example.com/your-very-long-and-complex-url-here"
                        />
                        <Link
                          size={18}
                          className="absolute left-3 top-1/2 text-muted-foreground -translate-y-1/2"
                        />
                      </div>
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />

                <span className="font-bold text-muted-foreground text-xs uppercase tracking-wider">
                  Advanced Options
                </span>
                <Separator />

                <section className="w-full flex justify-between gap-4">
                  <Controller
                    name="short_url"
                    control={singleUrlForm.control}
                    render={({ field, fieldState }) => (
                      <Field className="flex-1">
                        <FieldLabel
                          htmlFor={field.name}
                          className="font-bold text-sm"
                        >
                          Custom Alias (Optional)
                        </FieldLabel>
                        <div className="relative">
                          <span className="text-xs absolute -translate-y-1/2 top-1/2 left-3 text-muted-foreground">
                            {hostname}/
                          </span>
                          <Separator
                            orientation="vertical"
                            className="absolute -translate-y-1/2 top-1/2 left-18 h-6"
                          />
                          <Input
                            {...field}
                            id={field.name}
                            aria-invalid={fieldState.invalid}
                            className="pl-20 text-sm h-12 bg-surface"
                            placeholder="my-cool-link"
                          />
                        </div>
                        {fieldState.invalid && (
                          <FieldError errors={[fieldState.error]} />
                        )}
                      </Field>
                    )}
                  />
                  <Controller
                    name="expiry_date"
                    control={singleUrlForm.control}
                    render={({ field, fieldState }) => (
                      <Field className="flex-1">
                        <FieldLabel
                          htmlFor={field.name}
                          className="font-bold text-sm"
                        >
                          Expiration Date
                        </FieldLabel>
                        <DatePicker
                          {...field}
                          id={field.name}
                          aria-invalid={fieldState.invalid}
                        />
                        {fieldState.invalid && (
                          <FieldError errors={[fieldState.error]} />
                        )}
                      </Field>
                    )}
                  />
                </section>

                <Separator />
              </>
            ) : (
              <>
                {/* Batch Mode Form */}
                <Controller
                  name="urls"
                  control={batchUrlForm.control}
                  render={({ field, fieldState }) => (
                    <Field>
                      <FieldLabel
                        htmlFor={field.name}
                        className="font-bold text-sm"
                      >
                        Batch URLs (JSON Format)
                      </FieldLabel>
                      <Textarea
                        {...field}
                        value={
                          typeof field.value === "string" ? field.value : ""
                        }
                        onChange={(e) => field.onChange(e.target.value)}
                        id={field.name}
                        aria-invalid={fieldState.invalid}
                        className="scrollbar-none [ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden resize-none h-60 overflow-y-scroll bg-surface"
                        placeholder={`[
    {
        "name": "My Link",
        "long_url": "https://www.example1.com",
        "short_url": "custom1",
        "expiry_date": "2024-12-31T23:59:59Z"
    },
    {
        "name": "My Link 2",
        "long_url": "https://www.example2.com"
    }
]`}
                      />
                      {fieldState.invalid && (
                        <FieldError errors={[fieldState.error]} />
                      )}
                    </Field>
                  )}
                />
                <Separator />
              </>
            )}
          </TabsContent>
          <TabsContent
            value="redirection"
            className="flex flex-col gap-4 overflow-y-auto flex-1 min-h-0"
          >
            <Separator className="w-full" />

            {/* Header */}
            <div className="flex items-start justify-between">
              <div>
                <h2 className="text-lg font-bold">
                  Conditional Redirection Rules
                </h2>
                <p className="text-sm text-muted-foreground">
                  Configure advanced routing based on visitor context.
                </p>
              </div>
              <div className="flex gap-2">
                <Button
                  size="sm"
                  className="gap-2 bg-primary"
                  onClick={() => setShowNewRuleForm(true)}
                  disabled={showNewRuleForm}
                >
                  <Plus size={16} />
                  NEW RULE
                </Button>
              </div>
            </div>

            {/* Rules List */}
            <div className="flex flex-col gap-3">
              {rules.map((rule, index) => (
                <RedirectionRuleCard
                  key={rule.id}
                  rule={rule}
                  ruleNumber={index + 1}
                  isExpanded={editingRuleId === rule.id}
                  onSave={handleSaveRule}
                  onDiscard={handleDiscardRule}
                />
              ))}

              {/* New Rule Form */}
              {showNewRuleForm && (
                <RedirectionRuleCard
                  ruleNumber={rules.length + 1}
                  isExpanded={true}
                  onSave={handleSaveRule}
                  onDiscard={handleDiscardRule}
                />
              )}
            </div>

            {/* Empty State */}
            {rules.length === 0 && !showNewRuleForm && (
              <div className="flex flex-col items-center justify-center py-12 text-center">
                <Layers size={48} className="text-muted-foreground mb-4" />
                <h3 className="font-bold text-lg mb-2">
                  No Redirection Rules Yet
                </h3>
                <p className="text-sm text-muted-foreground mb-4 max-w-md">
                  Create conditional rules to redirect visitors based on their
                  location, device, browser, and more.
                </p>
                <Button
                  size="sm"
                  className="gap-2"
                  onClick={() => setShowNewRuleForm(true)}
                >
                  <Plus size={16} />
                  Create Your First Rule
                </Button>
              </div>
            )}
          </TabsContent>
        </Tabs>
        <div className="place-self-end flex items-center gap-2 shrink-0 pt-4 ">
          <Button size="lg" variant="ghost">
            Cancel
          </Button>
          <Button
            size="lg"
            className="bg-gradient-blue-purple hover:shadow-glow-blue transition-shadow"
            onClick={
              batchMode
                ? batchUrlForm.handleSubmit(onSubmitBatch)
                : singleUrlForm.handleSubmit(onSubmitSingle as any)
            }
          >
            Create Link
            <Zap size={16} className="ml-1" />
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
