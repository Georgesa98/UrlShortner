"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Link2,
  Zap,
  Users,
  BarChart3,
  Shield,
  Sparkles,
  User,
  ArrowRight,
} from "lucide-react";

export default function AboutPage() {
  const stats = [
    {
      icon: Link2,
      label: "LINKS SHORTENED",
      value: "1M+",
    },
    {
      icon: Zap,
      label: "UPTIME RELIABILITY",
      value: "99.9%",
    },
    {
      icon: Users,
      label: "HAPPY USERS",
      value: "500k",
    },
  ];

  const features = [
    {
      icon: Zap,
      title: "Lightning Fast",
      description:
        "Our global CDN ensures your links redirect instantly, no matter where your audience is located.",
    },
    {
      icon: BarChart3,
      title: "Deep Analytics",
      description:
        "Gain insights into who clicks your links, from where, and on what device with our detailed dashboard.",
    },
    {
      icon: Shield,
      title: "Secure & Reliable",
      description:
        "Enterprise-grade security and 99.9% uptime guarantee keeps your links safe and accessible.",
    },
  ];

  return (
    <div className="flex flex-col items-center min-h-screen py-20">
      {/* Hero Section */}
      <div className="w-full max-w-6xl px-8 mb-20 text-center">
        <Badge
          variant="outline"
          className="mb-6 text-primary border-primary/30"
        >
          EST. 2024
        </Badge>
        <h1 className="text-4xl md:text-6xl font-bold text-foreground mb-6 leading-tight">
          Making the web shorter,{" "}
          <span className="text-gradient-blue-purple">one link at a time.</span>
        </h1>
        <p className="text-muted-foreground text-lg max-w-3xl mx-auto">
          We're on a mission to organize the world's information by making links
          easier to share, track, and manage.
        </p>
      </div>

      {/* Stats Cards Section */}
      <div className="w-full max-w-6xl px-8 mb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {stats.map((stat) => {
            const Icon = stat.icon;
            return (
              <Card
                key={stat.label}
                className="text-center hover:bg-surface-hover transition-colors"
              >
                <CardHeader>
                  <div className="flex justify-center mb-3">
                    <div className="p-3 rounded-lg bg-primary/10">
                      <Icon className="size-6 text-primary" />
                    </div>
                  </div>
                  <CardDescription className="text-xs font-semibold tracking-wider">
                    {stat.label}
                  </CardDescription>
                  <CardTitle className="text-3xl">{stat.value}</CardTitle>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Our Mission Section */}
      <div className="w-full max-w-6xl px-8 mb-20">
        <h2 className="text-3xl font-bold text-foreground mb-8">Our Mission</h2>
        <Card className="overflow-hidden">
          <div className="grid md:grid-cols-2">
            <div className="relative p-8 border-l-4 border-primary">
              <CardHeader className="px-0 pt-0">
                <CardTitle className="text-2xl mb-4">
                  Simplifying Digital Sharing
                </CardTitle>
                <CardDescription className="text-base leading-relaxed mb-6">
                  Our mission is to simplify digital sharing while providing
                  powerful insights into audience behavior. We believe in speed,
                  reliability, and the power of data. We are building the
                  infrastructure that connects people to content seamlessly.
                </CardDescription>
              </CardHeader>
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  <div className="size-8 rounded-full bg-primary/20 border-2 border-card flex items-center justify-center">
                    <User className="size-4 text-primary" />
                  </div>
                  <div className="size-8 rounded-full bg-purple-500/20 border-2 border-card flex items-center justify-center">
                    <User className="size-4 text-purple-400" />
                  </div>
                  <div className="size-8 rounded-full bg-blue-500/20 border-2 border-card flex items-center justify-center">
                    <User className="size-4 text-blue-400" />
                  </div>
                </div>
                <span className="text-sm text-muted-foreground">
                  Trusted by thousands
                </span>
              </div>
            </div>
            <div className="relative bg-gradient-to-br from-primary/10 via-purple-500/10 to-transparent p-8 flex items-center justify-center min-h-[300px]">
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-purple-500/20 blur-3xl" />
                <Sparkles className="size-24 text-primary/40 relative z-10" />
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Why Choose Section */}
      <div className="w-full max-w-6xl px-8 mb-20">
        <div className="text-center mb-10">
          <h2 className="text-3xl font-bold text-foreground mb-3">
            Why choose LinkShortener?
          </h2>
          <p className="text-muted-foreground">
            Built for performance, designed for you.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {features.map((feature) => {
            const Icon = feature.icon;
            return (
              <Card
                key={feature.title}
                className="text-center hover:bg-surface-hover transition-colors"
              >
                <CardHeader>
                  <div className="flex justify-center mb-4">
                    <div className="p-3 rounded-lg bg-primary/10">
                      <Icon className="size-6 text-primary" />
                    </div>
                  </div>
                  <CardTitle className="text-xl mb-3">
                    {feature.title}
                  </CardTitle>
                  <CardDescription className="text-sm leading-relaxed">
                    {feature.description}
                  </CardDescription>
                </CardHeader>
              </Card>
            );
          })}
        </div>
      </div>

      {/* Meet the Team Section */}
      <div className="w-full max-w-6xl px-8 mb-20">
        <div className="flex items-center justify-between mb-10">
          <h2 className="text-3xl font-bold text-foreground">Meet the Team</h2>
          <Button variant="ghost" className="gap-2">
            Join us <ArrowRight className="size-4" />
          </Button>
        </div>
        <div className="flex justify-center">
          <Card className="w-full max-w-xs text-center hover:bg-surface-hover transition-colors">
            <CardHeader>
              <div className="flex justify-center mb-4">
                <div className="size-32 rounded-2xl bg-gradient-to-br from-primary/20 to-purple-500/20 flex items-center justify-center">
                  <User className="size-16 text-primary" />
                </div>
              </div>
              <CardTitle className="text-xl">George Salebe</CardTitle>
              <CardDescription>Founder & Developer</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </div>

      {/* CTA Section */}
      <div className="w-full max-w-4xl px-8">
        <Card className="border-border text-center">
          <CardHeader>
            <div className="flex justify-center mb-4">
              <div className="p-3 rounded-full bg-primary/10">
                <Sparkles className="size-8 text-primary" />
              </div>
            </div>
            <CardTitle className="text-3xl mb-3">
              Ready to optimize your links?
            </CardTitle>
            <CardDescription className="text-base mb-6">
              Join over 500,000 marketers and creators using LinkShortener
              today.
            </CardDescription>
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              <Button size="lg" className="px-8">
                Get Started for Free
              </Button>
              <Button size="lg" variant="outline" className="px-8">
                Contact Sales
              </Button>
            </div>
          </CardHeader>
        </Card>
      </div>
    </div>
  );
}
