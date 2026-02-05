"use client";

import {
  ArrowRight,
  Info,
  Layers,
  Link,
  List,
  MousePointerClick,
  Zap,
  Loader2,
} from "lucide-react";
import { Card, CardContent } from "../ui/card";
import { Input } from "../ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../ui/tabs";
import { Button } from "../ui/button";
import { Separator } from "../ui/separator";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "../ui/accordion";
import { Label } from "../ui/label";
import { Textarea } from "../ui/textarea";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import {
  landingPageSingleUrlSchema,
  landingPageBatchUrlSchema,
} from "./schema";
import SignupPromptDialog from "./SignupPromptDialog";
import { getAuthStatus } from "@/lib/authStatus";
import type { z } from "zod";

export default function HeroSection({ className }: { className?: string }) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSignupDialogOpen, setIsSignupDialogOpen] = useState(false);
  const [auth, setAuth] = useState<any>();
  const router = useRouter();

  useEffect(() => {
    async function checkAuth() {
      const status = await getAuthStatus();
      setAuth(status);
    }
    checkAuth();
  }, []);

  const singleUrlForm = useForm<z.infer<typeof landingPageSingleUrlSchema>>({
    resolver: zodResolver(landingPageSingleUrlSchema),
    defaultValues: {
      long_url: "",
      short_url: "",
      expiry_date: "",
    },
  });

  const batchUrlForm = useForm<z.infer<typeof landingPageBatchUrlSchema>>({
    resolver: zodResolver(landingPageBatchUrlSchema),
    defaultValues: {
      urls: "",
    },
  });

  const handleSingleSubmit = async (
    data: z.infer<typeof landingPageSingleUrlSchema>,
  ) => {
    setIsProcessing(true);

    // If user is logged in, redirect to dashboard where they can create URLs
    if (auth?.isLoggedIn) {
      setTimeout(() => {
        router.push(auth.isAdmin ? "/admin/urls-management" : "/urls");
      }, 500);
    } else {
      // Show signup dialog for non-logged-in users
      setTimeout(() => {
        setIsProcessing(false);
        setIsSignupDialogOpen(true);
      }, 500);
    }
  };

  const handleBatchSubmit = async (
    data: z.infer<typeof landingPageBatchUrlSchema>,
  ) => {
    setIsProcessing(true);

    // If user is logged in, redirect to dashboard where they can create URLs
    if (auth?.isLoggedIn) {
      setTimeout(() => {
        router.push(auth.isAdmin ? "/admin/dashboard" : "/urls");
      }, 500);
    } else {
      // Show signup dialog for non-logged-in users
      setTimeout(() => {
        setIsProcessing(false);
        setIsSignupDialogOpen(true);
      }, 500);
    }
  };

  return (
    <section
      className={`text-center flex flex-col items-center gap-6 ${className}`}
    >
      <h1 className="text-5xl font-extrabold">
        Make every <span className="text-gradient-blue-purple">connection</span>{" "}
        count.
      </h1>
      <div>
        <p className="text-muted-foreground">
          The most powerful URL shortener out there.
        </p>
        <p className="text-muted-foreground">
          Built for modern teams who needs reliability at scale.
        </p>
      </div>
      <Card className="w-[90%]">
        <CardContent>
          <Tabs defaultValue="single">
            <TabsList>
              <TabsTrigger value="single">Single Url</TabsTrigger>
              <TabsTrigger value="batch">Batch Mode</TabsTrigger>
            </TabsList>
            <TabsContent value="single" className="flex flex-col gap-2">
              <form
                onSubmit={singleUrlForm.handleSubmit(handleSingleSubmit)}
                className="flex flex-col gap-2"
              >
                <div className="flex flex-col gap-2">
                  <div className="flex gap-2">
                    <div className="relative w-full flex flex-col gap-1">
                      <div className="relative w-full">
                        <Link
                          className="absolute left-2 top-4 opacity-80"
                          size={18}
                        />
                        <Input
                          {...singleUrlForm.register("long_url")}
                          placeholder="Paste a long url to shorten..."
                          className="bg-background px-8 py-6"
                          disabled={isProcessing}
                        />
                      </div>
                      {singleUrlForm.formState.errors.long_url && (
                        <p className="text-destructive text-xs px-2">
                          {singleUrlForm.formState.errors.long_url.message}
                        </p>
                      )}
                    </div>
                    <Button
                      type="submit"
                      className="py-6"
                      disabled={isProcessing}
                    >
                      {isProcessing ? (
                        <>
                          <Loader2 className="animate-spin" />
                          Processing
                        </>
                      ) : (
                        <>
                          Shorten URL <ArrowRight />
                        </>
                      )}
                    </Button>
                  </div>
                </div>
                <Accordion
                  collapsible
                  type="single"
                  className="bg-background rounded-lg"
                >
                  <AccordionItem value="advance-single">
                    <AccordionTrigger className="px-4">
                      <span className="flex items-center gap-2">
                        <List size="18" />
                        Advance Options
                      </span>
                    </AccordionTrigger>
                    <Separator className="w-full" />
                    <AccordionContent className="flex flex-col px-6 py-4">
                      <div className="flex gap-4">
                        <div className="flex-1 flex flex-col gap-2">
                          <Label className="self-center">Custom Alias</Label>
                          <div className="flex flex-col gap-1">
                            <div className="relative w-full">
                              <span className="absolute left-2 top-2 text-muted-foreground">
                                short.co/
                              </span>
                              <Separator
                                orientation="vertical"
                                className="absolute left-18"
                              />
                              <Input
                                {...singleUrlForm.register("short_url")}
                                placeholder="custom-link"
                                className="pl-19"
                                disabled={isProcessing}
                              />
                            </div>
                            {singleUrlForm.formState.errors.short_url && (
                              <p className="text-destructive text-xs px-2">
                                {
                                  singleUrlForm.formState.errors.short_url
                                    .message
                                }
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="flex-1 flex flex-col gap-2">
                          <Label className="self-center">Expiration Date</Label>
                          <Input
                            {...singleUrlForm.register("expiry_date")}
                            type="date"
                            className="text-muted-foreground"
                            disabled={isProcessing}
                          />
                        </div>
                      </div>
                    </AccordionContent>
                  </AccordionItem>
                </Accordion>
              </form>
            </TabsContent>
            <TabsContent value="batch" className="w-full flex flex-col gap-4">
              <form
                onSubmit={batchUrlForm.handleSubmit(handleBatchSubmit)}
                className="w-full flex flex-col gap-4"
              >
                <div className="flex flex-col gap-1">
                  <Textarea
                    {...batchUrlForm.register("urls")}
                    className="bg-background resize-none max-w-150 h-60 overflow-y-scroll"
                    placeholder={`[
    {
        "long_url": "https://www.example1.com",
        "short_url": "custom1",
        "expiry_date": "2024-12-31T23:59:59Z"
    },
    {
        "long_url": "https://www.example2.com",
        "short_url": "custom2"
    }
]`}
                    disabled={isProcessing}
                  />
                  {batchUrlForm.formState.errors.urls && (
                    <p className="text-destructive text-xs px-2">
                      {batchUrlForm.formState.errors.urls.message}
                    </p>
                  )}
                </div>
                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Info className="stroke-brand-blue" size="18" />
                    free plan limited to 10 links per batch
                  </p>
                  <Button
                    type="submit"
                    className="py-6"
                    size="lg"
                    disabled={isProcessing}
                  >
                    {isProcessing ? (
                      <>
                        <Loader2 className="animate-spin" />
                        Processing
                      </>
                    ) : (
                      <>
                        Shorten Batch <Layers />
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
      <Separator />
      <div className="flex justify-center gap-10 w-full text-start">
        <div className="flex items-center gap-2">
          <div className="bg-[#161e2c] p-2 rounded-full flex justify-center items-center">
            <Link className="text-brand-blue" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold">1M+</span>
            <span className="text-muted-foreground">Links Shortened</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="bg-[#0f211d] p-2 rounded-full flex justify-center items-center">
            <MousePointerClick className="text-green-500" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold">50M+</span>
            <span className="text-muted-foreground">Clicks Tracked</span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div className="bg-[#1d192b] p-2 rounded-full flex justify-center items-center">
            <Zap className="text-brand-purple" />
          </div>
          <div className="flex flex-col">
            <span className="font-bold">99.9%</span>
            <span className="text-muted-foreground">Uptime</span>
          </div>
        </div>
      </div>

      <SignupPromptDialog
        open={isSignupDialogOpen}
        onOpenChange={setIsSignupDialogOpen}
      />
    </section>
  );
}
