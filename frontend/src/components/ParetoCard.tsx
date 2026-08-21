"use client";

import React from "react";
import { AlertCircle, Check, Zap, Utensils, ShoppingBag } from "lucide-react";

interface ParetoOption {
  title?: string;
  protein?: number;
  calories?: number;
  cost?: number;
  description?: string;
  food?: any;
  instamart?: any[];
  restaurant_dish?: any;
  boosters?: any[];
  total_protein?: number;
  total_calories?: number;
  total_p?: number;
  total_c?: number;
  subtotal?: number;
  total_payable?: number;
}

interface ParetoCardProps {
  options: {
    option_a?: ParetoOption;
    option_b?: ParetoOption;
  };
  targetProtein: number;
  maxBudget: number;
  selectedOption: "A" | "B";
  onSelectOption: (opt: "A" | "B") => void;
  goalGapText?: string;
}

export const ParetoCard: React.FC<ParetoCardProps> = ({
  options,
  targetProtein,
  maxBudget,
  selectedOption,
  onSelectOption,
  goalGapText,
}) => {
  const optA = options?.option_a || {};
  const optB = options?.option_b || {};

  const optAFoodDish = optA.restaurant_dish || optA.food || {};
  const optABoosters: any[] = optA.boosters || optA.instamart || [];
  const optACost = optA.total_payable ?? optA.cost ?? 0;
  const optAOver = Math.max(0, optACost - maxBudget);
  const optAProtein = optA.total_protein ?? optA.total_p ?? optA.protein ?? targetProtein;
  const optAFoodName = optAFoodDish.name || "Restaurant Dish";
  const optAInstamartNames =
    optABoosters.length > 0
      ? optABoosters.map((b: any) => b.name).filter(Boolean).join(" + ")
      : "No add-ons (Base dish only)";

  const optBFoodDish = optB.restaurant_dish || optB.food || {};
  const optBBoosters: any[] = optB.boosters || optB.instamart || [];
  const optBCost = optB.total_payable ?? optB.cost ?? 0;
  const optBProtein = optB.total_protein ?? optB.total_p ?? optB.protein ?? 0;
  const optBFoodName = optBFoodDish.name || "Standalone Base Dish";
  const optBInstamartNames =
    optBBoosters.length > 0
      ? optBBoosters.map((b: any) => b.name).filter(Boolean).join(" + ")
      : "No add-ons (Base dish only)";

  const bProteinGap = Math.max(0, roundOne(targetProtein - optBProtein));
  const defaultHeader =
    bProteinGap > 0
      ? `Goal Gap: -${bProteinGap}g Protein under strict budget`
      : "No exact match for your strict budget";

  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-2xl p-5 shadow-lg space-y-4">
      {/* Alert Header */}
      <div className="space-y-1">
        <div className="flex items-center gap-2 text-zinc-100 font-extrabold text-sm sm:text-base">
          <div className="bg-orange-500/10 text-[#FC8019] p-1.5 rounded-md">
            <AlertCircle className="w-4 h-4 shrink-0" />
          </div>
          <span>{goalGapText || defaultHeader}</span>
        </div>
        <p className="text-xs text-zinc-400 leading-relaxed">
          We found two close options. Choose whether you&apos;d rather stretch your budget slightly or get the highest protein possible within your limit.
        </p>
      </div>

      {/* Side-by-Side Trade-off Options */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Option A: Hit Protein Goal */}
        <div
          onClick={() => onSelectOption("A")}
          className={`cursor-pointer rounded-2xl p-4 transition-all duration-200 flex flex-col justify-between space-y-3 ${
            selectedOption === "A"
              ? "border-[#FC8019] bg-zinc-900/90 ring-1 ring-[#FC8019] shadow-xl"
              : "bg-zinc-900/60 border border-zinc-800 hover:border-zinc-700 opacity-80"
          }`}
        >
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-extrabold text-sm text-zinc-100">
                Hit Protein Goal {optAOver > 0 ? `(+₹${optAOver} over budget)` : ""}
              </span>
              {selectedOption === "A" && (
                <span className="bg-[#FC8019] text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                  <Check className="w-3 h-3" /> Selected
                </span>
              )}
            </div>

            <p className="text-xs text-zinc-400 leading-relaxed">
              Delivers {optAProtein}g protein by adjusting budget limit to ₹{optACost}.
            </p>

            {/* Tangible Food Items Mini-Breakdown */}
            <div className="pt-2 space-y-1.5 border-t border-zinc-800/80 text-xs">
              <div className="flex items-start gap-1.5 text-zinc-300">
                <Utensils className="w-3.5 h-3.5 text-[#FC8019] shrink-0 mt-0.5" />
                <span className="font-semibold text-zinc-200">{optAFoodName}</span>
              </div>
              <div className="flex items-start gap-1.5 text-zinc-400">
                <ShoppingBag className="w-3.5 h-3.5 text-zinc-400 shrink-0 mt-0.5" />
                <span>{optAInstamartNames}</span>
              </div>
              <div className="flex items-center gap-1 text-[11px] text-zinc-500 pt-0.5">
                <Zap className="w-3 h-3 text-[#FC8019]" />
                <span>25–30 mins combined delivery</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-zinc-800/60 font-mono text-xs">
            <span className="font-bold text-[#FC8019]">{optAProtein}g Protein</span>
            <span className="font-bold text-zinc-200">₹{optACost} Total</span>
          </div>
        </div>

        {/* Option B: Stay Within Budget */}
        <div
          onClick={() => onSelectOption("B")}
          className={`cursor-pointer rounded-2xl p-4 transition-all duration-200 flex flex-col justify-between space-y-3 ${
            selectedOption === "B"
              ? "border-[#FC8019] bg-zinc-900/90 ring-1 ring-[#FC8019] shadow-xl"
              : "bg-zinc-900/60 border border-zinc-800 hover:border-zinc-700 opacity-80"
          }`}
        >
          <div className="space-y-2.5">
            <div className="flex items-center justify-between">
              <span className="font-extrabold text-sm text-zinc-100">
                Stay Within ₹{maxBudget} Budget
              </span>
              {selectedOption === "B" && (
                <span className="bg-[#FC8019] text-white text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                  <Check className="w-3 h-3" /> Selected
                </span>
              )}
            </div>

            <p className="text-xs text-zinc-400 leading-relaxed">
              Strictly respects your ₹{maxBudget} cap, delivering the maximum possible {optBProtein}g protein.
            </p>

            {/* Tangible Food Items Mini-Breakdown */}
            <div className="pt-2 space-y-1.5 border-t border-zinc-800/80 text-xs">
              <div className="flex items-start gap-1.5 text-zinc-300">
                <Utensils className="w-3.5 h-3.5 text-[#FC8019] shrink-0 mt-0.5" />
                <span className="font-semibold text-zinc-200">{optBFoodName}</span>
              </div>
              <div className="flex items-start gap-1.5 text-zinc-400">
                <ShoppingBag className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
                <span>{optBInstamartNames}</span>
              </div>
              <div className="flex items-center gap-1 text-[11px] text-zinc-500 pt-0.5">
                <Zap className="w-3 h-3 text-[#FC8019]" />
                <span>30 mins delivery</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between pt-2 border-t border-zinc-800/60 font-mono text-xs">
            <span className="font-bold text-[#FC8019]">{optBProtein}g Protein</span>
            <span className="font-bold text-zinc-200">₹{optBCost} Total</span>
          </div>
        </div>
      </div>
    </div>
  );
};

function roundOne(n: number) {
  return Math.round(n * 10) / 10;
}
