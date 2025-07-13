"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { cn } from "@/lib/utils";
import { CircleCheck, CircleHelp } from "lucide-react";
import { useState } from "react";

const tooltipContent = {
  modes: "Predefined trading modes to get started quickly.",
  builder: "Advanced strategy builder for custom trading strategies.",
  policy: "Vincent policy engine for automated decision making.",
  autonomy: "Full autonomy with custom rule sets and agent behavior.",
};

const YEARLY_DISCOUNT = 20;
const plans = [
  {
    name: "Starter",
    price: 0,
    description: "Access basic AI trading features and predefined modes.",
    features: [
      { title: "Kairos AI basic trading", tooltip: undefined },
      { title: "Predefined trading modes", tooltip: tooltipContent.modes },
      { title: "Community support" },
    ],
    buttonText: "Start for Free",
  },
  {
    name: "Pro",
    price: 50,
    isRecommended: true,
    description:
      "Unlock advanced strategy builder and Vincent policy engine.",
    features: [
      { title: "Kairos AI advanced trading", tooltip: undefined },
      { title: "Advanced strategy builder", tooltip: tooltipContent.builder },
      { title: "Vincent policy engine", tooltip: tooltipContent.policy },
      { title: "Priority support" },
    ],
    buttonText: "Upgrade to Pro",
    isPopular: true,
  },
  {
    name: "Enterprise",
    price: 200,
    description:
      "Full autonomy with custom rule sets and gated agent behavior.",
    features: [
      { title: "Kairos AI enterprise suite", tooltip: undefined },
      { title: "Custom rule sets", tooltip: tooltipContent.autonomy },
      { title: "Gated agent behavior", tooltip: tooltipContent.autonomy },
      { title: "Dedicated support" },
    ],
    buttonText: "Contact Sales",
  },
];

const Pricing = () => {
  const [selectedBillingPeriod, setSelectedBillingPeriod] = useState("monthly");

  return (
    <div
      id="pricing"
      className="flex flex-col items-center justify-center py-12 xs:py-20 px-6"
    >
      <h1 className="text-3xl xs:text-4xl md:text-5xl font-bold text-center tracking-tight">
        Pricing
      </h1>
      <Tabs
        value={selectedBillingPeriod}
        onValueChange={setSelectedBillingPeriod}
        className="mt-8"
      >
        <TabsList className="h-11 px-1.5 rounded-full bg-primary/5">
          <TabsTrigger value="monthly" className="py-1.5 rounded-full">
            Monthly
          </TabsTrigger>
          <TabsTrigger value="yearly" className="py-1.5 rounded-full">
            Yearly (Save {YEARLY_DISCOUNT}%)
          </TabsTrigger>
        </TabsList>
      </Tabs>
      <div className="mt-12 max-w-screen-lg mx-auto grid grid-cols-1 lg:grid-cols-3 items-center gap-8">
        {plans.map((plan) => (
          <div
            key={plan.name}
            className={cn("relative border rounded-xl p-6 bg-background/50", {
              "border-[2px] border-primary bg-background py-10": plan.isPopular,
            })}
          >
            {plan.isPopular && (
              <Badge className="absolute top-0 right-1/2 translate-x-1/2 -translate-y-1/2">
                Most Popular
              </Badge>
            )}
            <h3 className="text-lg font-medium">{plan.name}</h3>
            <p className="mt-2 text-4xl font-bold">
              {plan.price === 0 ? (
                "Free"
              ) : (
                <>
                  $
                  {selectedBillingPeriod === "monthly"
                    ? plan.price
                    : plan.price * ((100 - YEARLY_DISCOUNT) / 100)}
                  <span className="ml-1.5 text-sm text-muted-foreground font-normal">
                    /month
                  </span>
                </>
              )}
            </p>
            <p className="mt-4 font-medium text-muted-foreground">
              {plan.description}
            </p>

            <Button
              variant={plan.isPopular ? "default" : "outline"}
              size="lg"
              className="w-full mt-6 text-base"
            >
              {plan.buttonText}
            </Button>
            <Separator className="my-8" />
            <ul className="space-y-2">
              {plan.features.map((feature) => (
                <li key={feature.title} className="flex items-start gap-1.5">
                  <CircleCheck className="h-4 w-4 mt-1 text-green-600" />
                  {feature.title}
                  {feature.tooltip && (
                    <Tooltip>
                      <TooltipTrigger className="cursor-help">
                        <CircleHelp className="h-4 w-4 mt-1 text-gray-500" />
                      </TooltipTrigger>
                      <TooltipContent>{feature.tooltip}</TooltipContent>
                    </Tooltip>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Pricing;
