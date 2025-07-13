import {
  Bot,
  Database,
  Sliders,
  ShieldCheck,
  Wallet,
  BarChart2,
} from "lucide-react";
import React from "react";

const features = [
  {
    icon: Bot,
    title: "Autonomous AI Trading",
    description:
      "Make profitable trades based on past experiences and strategies.",
  },
  {
    icon: Database,
    title: "Hybrid Architecture",
    description:
      "Combines structured and vector databases for intelligent decision-making.",
  },
  {
    icon: Sliders,
    title: "Customizable Modes",
    description:
      "Operate in Normal, Average, or Aggressive modes with user-defined rules.",
  },
  {
    icon: ShieldCheck,
    title: "Vincent Policy Engine",
    description:
      "Enable advanced governance for risk management and strategy enforcement.",
  },
  {
    icon: Wallet,
    title: "Wallet-Based Personalization",
    description:
      "Securely sign in and unlock custom features using Lit Protocol.",
  },
  {
    icon: BarChart2,
    title: "Live Market Analysis",
    description:
      "Access real-time data from APIs like CoinGecko, TAAPI, and more.",
  },
];

const Features = () => {
  return (
    <div id="features" className="w-full py-12 xs:py-20 px-6">
      <h2 className="text-3xl xs:text-4xl sm:text-5xl font-bold tracking-tight text-center">
        Kairos AI Features
      </h2>
      <div className="w-full max-w-screen-lg mx-auto mt-10 sm:mt-16 grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature) => (
          <div
            key={feature.title}
            className="flex flex-col bg-background border rounded-xl py-6 px-5"
          >
            <div className="mb-3 h-10 w-10 flex items-center justify-center bg-muted rounded-full">
              <feature.icon className="h-6 w-6" />
            </div>
            <span className="text-lg font-semibold">{feature.title}</span>
            <p className="mt-1 text-foreground/80 text-[15px]">
              {feature.description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Features;
