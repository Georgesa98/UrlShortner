"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import {
  Search,
  Sparkles,
  FileText,
  BarChart3,
  Settings,
  Ticket,
  MessageCircle,
} from "lucide-react";

export default function HelpPage() {
  const categories = [
    {
      icon: Sparkles,
      title: "Getting Started",
      description:
        "Learn the basics of creating, editing and managing your first short links.",
    },
    {
      icon: FileText,
      title: "Custom Domains",
      description:
        "Set up your own branded domains (e.g., link.brand.com) for professional links.",
    },
    {
      icon: BarChart3,
      title: "Analytics",
      description:
        "Deep dive into your click data, visitor locations, devices, and traffic sources.",
    },
    {
      icon: Settings,
      title: "API & Integrations",
      description:
        "Developer documentation and keys for integrating our API into your apps.",
    },
  ];

  const faqs = [
    {
      question: "How do I change the destination URL?",
      answer:
        "You can change the destination URL by navigating to your links dashboard, selecting the link you want to edit, and clicking the 'Edit' button. From there, you can update the destination URL and save your changes.",
    },
    {
      question: "Why is my link flagged as spam?",
      answer:
        "Links may be flagged as spam if they contain suspicious content, redirect to known malicious sites, or violate our terms of service. If you believe this is an error, please contact our support team for review.",
    },
    {
      question: "Can I delete a short link?",
      answer:
        "Yes, you can delete any short link from your dashboard. However, please note that once deleted, the link will no longer work and this action cannot be undone. All analytics data associated with the link will be permanently removed.",
    },
    {
      question: "Do you offer an API for developers?",
      answer:
        "Yes! We offer a comprehensive REST API for developers. You can find full documentation, authentication details, and code examples in our API & Integrations section. API keys can be generated from your account settings.",
    },
  ];

  return (
    <div className="flex flex-col items-center min-h-screen py-20">
      {/* Hero Section */}
      <div className="w-full max-w-6xl px-8 mb-16">
        <div className="flex flex-col items-center text-center mb-8">
          <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
            How can we help you today?
          </h1>
          <p className="text-muted-foreground text-lg max-w-2xl">
            Search our knowledge base for guides, API docs, and answers.
          </p>
        </div>

        {/* Search Bar */}
        <div className="flex gap-3 max-w-3xl mx-auto">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-5 text-muted-foreground" />
            <Input
              placeholder="Search for articles, guides, and FAQs..."
              className="pl-10 h-12"
            />
          </div>
          <Button size="lg" className="px-8">
            Search
          </Button>
        </div>
      </div>

      {/* Browse by Category Section */}
      <div className="w-full max-w-6xl px-8 mb-16">
        <h2 className="text-2xl font-bold text-foreground mb-6">
          Browse by Category
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {categories.map((category) => {
            const Icon = category.icon;
            return (
              <Card
                key={category.title}
                className="hover:bg-surface-hover transition-colors cursor-pointer"
              >
                <CardHeader>
                  <div className="mb-3">
                    <Icon className="size-8 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{category.title}</CardTitle>
                  <CardDescription>{category.description}</CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Frequently Asked Questions Section */}
      <div className="w-full max-w-4xl px-8 mb-16">
        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-foreground mb-2">
            Frequently Asked Questions
          </h2>
          <p className="text-muted-foreground">
            Quick answers to common questions about managing your links.
          </p>
        </div>
        <Accordion type="single" collapsible className="w-full">
          {faqs.map((faq, index) => (
            <AccordionItem key={index} value={`item-${index}`}>
              <AccordionTrigger className="text-left">
                {faq.question}
              </AccordionTrigger>
              <AccordionContent className="text-muted-foreground">
                {faq.answer}
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>

      {/* Still Need Help Section */}
      <div className="w-full max-w-4xl px-8">
        <Card className="border-border">
          <CardHeader className="text-center">
            <CardTitle className="text-2xl mb-2">Still need help?</CardTitle>
            <CardDescription className="text-base mb-6">
              Our support team is available 24/7 to assist you with any issues.
            </CardDescription>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="px-8">
                <Ticket className="mr-2" />
                Submit a Ticket
              </Button>
              <Button size="lg" variant="outline" className="px-8">
                <MessageCircle className="mr-2" />
                Live Chat
              </Button>
            </div>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}
