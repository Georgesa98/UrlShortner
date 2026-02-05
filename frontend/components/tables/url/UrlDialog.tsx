import {
  createBatchLinkFormSchema,
  createLinkFormSchema,
  updateLinkFormSchema,
} from "@/app/(user)/urls/schema";
import {
  batchShortenUrlAction,
  createShortUrlAction,
  updateShortUrlAction,
  fetchRedirectionRulesAction,
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
import { useState, useCallback, useEffect } from "react";
import { useForm } from "react-hook-form";
import { toast } from "sonner";
import z from "zod";
import { GeneralSettingsTab } from "./components/GeneralSettingsTab";
import { RedirectionRulesTab } from "./components/RedirectionRulesTab";
import { UrlDialogFooter } from "./components/UrlDialogFooter";
import { UrlResponse } from "@/api-types";

interface UrlDialogProps {
  mode: "create" | "update";
  urlData?: UrlResponse;
  onSuccess?: () => void;
  trigger?: React.ReactNode;
  buttonClassName?: string;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
}

export default function UrlDialog({
  mode,
  urlData,
  onSuccess,
  trigger,
  buttonClassName,
  open: controlledOpen,
  onOpenChange: controlledOnOpenChange,
}: UrlDialogProps) {
  // State management
  const [internalOpen, setInternalOpen] = useState(false);
  const [activeTab, setActiveTab] = useState<string>("general");
  const [batchMode, setBatchMode] = useState<boolean>(false);
  const [rules, setRules] = useState<RedirectionRule[]>([]);
  const [showNewRuleForm, setShowNewRuleForm] = useState<boolean>(false);
  const [editingRuleId, setEditingRuleId] = useState<string | null>(null);
  const [isLoadingRules, setIsLoadingRules] = useState<boolean>(false);

  // Determine if dialog state is controlled
  const isControlled = controlledOpen !== undefined;
  const open = isControlled ? controlledOpen : internalOpen;
  const setOpen = isControlled ? controlledOnOpenChange || (() => {}) : setInternalOpen;

  // Hooks
  const hostname = useHostname();
  const router = useRouter();

  // Disable batch mode for update
  const isBatchModeAvailable = mode === "create";

  // Forms
  const batchUrlForm = useForm({
    resolver: zodResolver(createBatchLinkFormSchema),
    defaultValues: {
      urls: "",
    },
  });

  const singleUrlForm = useForm<z.infer<typeof createLinkFormSchema | typeof updateLinkFormSchema>>({
    resolver: zodResolver(mode === "create" ? createLinkFormSchema : updateLinkFormSchema),
    defaultValues: {
      name: "",
      long_url: "",
      short_url: "",
      expiry_date: new Date(),
      redirection_rules: [],
    },
  });

  // Fetch and populate data when in update mode
  useEffect(() => {
    if (mode === "update" && urlData && open) {
      // Pre-populate form with existing data
      singleUrlForm.reset({
        name: urlData.name || "",
        long_url: urlData.long_url,
        short_url: urlData.short_url,
        expiry_date: urlData.expiry_date ? new Date(urlData.expiry_date) : undefined,
      });

      // Fetch redirection rules
      const fetchRules = async () => {
        setIsLoadingRules(true);
        const result = await fetchRedirectionRulesAction(urlData.id);
        if (result.success && result.data) {
          setRules(result.data);
        }
        setIsLoadingRules(false);
      };
      fetchRules();
    } else if (mode === "create" && open) {
      // Reset form for create mode
      singleUrlForm.reset({
        name: "",
        long_url: "",
        short_url: "",
        expiry_date: new Date(),
        redirection_rules: [],
      });
      setRules([]);
    }
  }, [mode, urlData, open]);

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
      setOpen(false);
      if (onSuccess) onSuccess();
      setTimeout(() => {
        router.refresh();
      }, 1000);
    } else {
      toast.error(message || "Failed to create link");
    }
  };

  const onSubmitUpdate = async (data: z.infer<typeof updateLinkFormSchema>) => {
    if (!urlData) return;
    
    const { message, status } = await updateShortUrlAction({
      short_url: urlData.short_url,
      name: data.name || "",
      long_url: data.long_url,
      expiry_date: data.expiry_date?.toISOString() || "",
      redirection_rules: rules,
    });
    if (status === 200) {
      toast.success("Link updated successfully");
      setOpen(false);
      if (onSuccess) onSuccess();
      setTimeout(() => {
        router.refresh();
      }, 1000);
    } else {
      toast.error(message || "Failed to update link");
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
      setOpen(false);
      if (onSuccess) onSuccess();
      setTimeout(() => {
        router.refresh();
      }, 1000);
    } else {
      toast.error(message || "Failed to create batch links");
    }
  };

  const handleSubmit = () => {
    if (mode === "update") {
      singleUrlForm.handleSubmit(onSubmitUpdate as any)();
    } else if (batchMode) {
      batchUrlForm.handleSubmit(onSubmitBatch as any)();
    } else {
      singleUrlForm.handleSubmit(onSubmitSingle as any)();
    }
  };

  const dialogTitle = mode === "create" ? "Create New Link" : "Edit Link";
  const dialogDescription = mode === "create" 
    ? "Shorten your long URLs and customize your links."
    : "Update your link settings and redirection rules.";

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      {trigger ? (
        <DialogTrigger asChild>
          {trigger}
        </DialogTrigger>
      ) : (
        <DialogTrigger asChild>
          <Button className={buttonClassName}>
            <Plus />
            Create New
          </Button>
        </DialogTrigger>
      )}
      <DialogContent className="min-w-3xl max-h-[90vh] flex flex-col overflow-hidden">
        <DialogTitle hidden>{dialogTitle}</DialogTitle>
        <DialogHeader className="gap-1 shrink-0">
          <h1 className="text-2xl font-bold">{dialogTitle}</h1>
          <p className="text-sm text-muted-foreground">
            {dialogDescription}
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
                batchMode={batchMode && isBatchModeAvailable}
                setBatchMode={isBatchModeAvailable ? setBatchMode : () => {}}
                singleUrlForm={singleUrlForm}
                batchUrlForm={batchUrlForm as any}
                hostname={hostname}
                isUpdateMode={mode === "update"}
                hideBatchToggle={!isBatchModeAvailable}
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
                isLoading={isLoadingRules}
              />
            )}
          </div>
        </Tabs>

        <UrlDialogFooter
          mode={mode}
          batchMode={batchMode && isBatchModeAvailable}
          onCancel={() => setOpen(false)}
          onSubmit={handleSubmit}
        />
      </DialogContent>
    </Dialog>
  );
}
