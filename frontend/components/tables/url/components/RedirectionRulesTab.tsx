import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import {
    RedirectionRule,
    RedirectionRuleCard,
} from "@/components/tables/url/RedirectionRuleCard";
import { Layers, Plus } from "lucide-react";

interface RedirectionRulesTabProps {
    rules: RedirectionRule[];
    showNewRuleForm: boolean;
    editingRuleId: string | null;
    onSaveRule: (rule: RedirectionRule) => void;
    onDiscardRule: () => void;
    onShowNewRuleForm: () => void;
    isLoading?: boolean;
}

export function RedirectionRulesTab({
    rules,
    showNewRuleForm,
    editingRuleId,
    onSaveRule,
    onDiscardRule,
    onShowNewRuleForm,
    isLoading = false,
}: RedirectionRulesTabProps) {
    return (
        <>
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
                        onClick={onShowNewRuleForm}
                        disabled={showNewRuleForm}
                    >
                        <Plus size={16} />
                        NEW RULE
                    </Button>
                </div>
            </div>

            {/* Rules List */}
            <div className="flex flex-col gap-3">
                {isLoading ? (
                    <div className="text-center py-4 text-muted-foreground">
                        Loading redirection rules...
                    </div>
                ) : (
                    rules.map((rule, index) => (
                        <RedirectionRuleCard
                            key={rule.id}
                            rule={rule}
                            ruleNumber={index + 1}
                            isExpanded={editingRuleId === rule.id}
                            onSave={onSaveRule}
                            onDiscard={onDiscardRule}
                        />
                    ))
                )}

                {/* New Rule Form */}
                {showNewRuleForm && (
                    <RedirectionRuleCard
                        ruleNumber={rules.length + 1}
                        isExpanded={true}
                        onSave={onSaveRule}
                        onDiscard={onDiscardRule}
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
                        Create conditional rules to redirect visitors based on
                        their location, device, browser, and more.
                    </p>
                    <Button
                        size="sm"
                        className="gap-2"
                        onClick={onShowNewRuleForm}
                    >
                        <Plus size={16} />
                        Create Your First Rule
                    </Button>
                </div>
            )}
        </>
    );
}
