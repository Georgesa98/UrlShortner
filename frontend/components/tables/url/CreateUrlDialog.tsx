import {
  createBatchLinkFormSchema,
  createLinkFormSchema,
} from "@/app/(user)/urls/schema";
import {
  batchShortenUrlAction,
  createShortUrlAction,
} from "@/app/(user)/urls/server";
import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Tabs, TabsTrigger } from "@/components/ui/tabs";
import { RedirectionRule } from "@/components/tables/url/RedirectionRuleCard";
import useHostname from "@/hooks/useHostname";
import { zodResolver } from "@hookform/resolvers/zod";
import { TabsList } from "@radix-ui/react-tabs";
import { Plus, Settings, Layers } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, useCallback } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";
import { GeneralSettingsTab } from "./components/GeneralSettingsTab";
import { RedirectionRulesTab } from "./components/RedirectionRulesTab";
import { CreateUrlDialogFooter } from "./components/CreateUrlDialogFooter";

export default function CreateUrlDialog({
  buttonClassName,
}: {
  buttonClassName: string;
}) {
  // State management
  const [activeTab, setActiveTab] = useState<string>("general");
  const [batchMode, setBatchMode] = useState<boolean>(false);
  const [rules, setRules] = useState<RedirectionRule[]>([]);
  const [showNewRuleForm, setShowNewRuleForm] = useState<boolean>(false);
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null);

  // Hooks
  const hostname = useHostname();
  const router = useRouter();

  // Forms
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
      redirection_rules: [],
    },
  });

  // PERFORMANCE: Memoize rule handlers to prevent unnecessary re-renders
  const handleSaveRule = useCallback((rule: RedirectionRule) => {
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
  }, []);

  const handleDiscardRule = useCallback(() => {
    setShowNewRuleForm(false);
    setEditingRuleId(null);
  }, []);

  const handleShowNewRuleForm = useCallback(() => {
    setShowNewRuleForm(true);
  }, []);

  // Form submission handlers
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

  const handleSubmit = () => {
    if (batchMode) {
      batchUrlForm.handleSubmit(onSubmitBatch as any)();
    } else {
      singleUrlForm.handleSubmit(onSubmitSingle as any)();
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
        <DialogTitle hidden>Create New Link</DialogTitle>
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

          {/* PERFORMANCE: Conditional rendering - only render active tab */}
          <div className="flex flex-col gap-4 overflow-y-auto flex-1 min-h-0">
            {activeTab === "general" && (
              <GeneralSettingsTab
                batchMode={batchMode}
                setBatchMode={setBatchMode}
                singleUrlForm={singleUrlForm}
                batchUrlForm={batchUrlForm as any}
                hostname={hostname}
              />
            )}

            {activeTab === "redirection" && (
              <RedirectionRulesTab
                rules={rules}
                showNewRuleForm={showNewRuleForm}
                editingRuleId={editingRuleId}
                onSaveRule={handleSaveRule}
                onDiscardRule={handleDiscardRule}
                onShowNewRuleForm={handleShowNewRuleForm}
              />
            )}
          </div>
        </Tabs>

        <CreateUrlDialogFooter
          batchMode={batchMode}
          onCancel={() => {}}
          onSubmit={handleSubmit}
        />
      </DialogContent>
    </Dialog>
  );
}
