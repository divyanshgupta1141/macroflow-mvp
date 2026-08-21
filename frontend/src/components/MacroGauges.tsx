"use client";

import React from "react";
import { motion } from "framer-motion";
import { Flame, Dumbbell, Wheat, Droplet, BarChart3 } from "lucide-react";
import { NumberTicker } from "./ui/NumberTicker";

interface MacroGaugesProps {
  recommendation?: any;
  protein?: number;
  targetProtein?: number;
  calories?: number;
  maxCalories?: number;
  carbs?: number;
  fats?: number;
}

export const MacroGauges: React.FC<MacroGaugesProps> = ({
  recommendation,
  protein = 0,
  targetProtein = 60,
  calories = 0,
  maxCalories = 650,
  carbs = 0,
  fats = 0,
}) => {
  const pVal = recommendation?.total_protein ?? recommendation?.total_p ?? protein;
  const cVal = recommendation?.total_calories ?? recommendation?.total_c ?? calories;
  const carbsVal = recommendation?.total_carbs ?? carbs;
  const fatsVal = recommendation?.total_fats ?? fats;

  const proteinPercent = Math.min(100, Math.round((pVal / Math.max(1, targetProtein)) * 100));
  const caloriesPercent = Math.min(100, Math.round((cVal / Math.max(1, maxCalories)) * 100));
  const carbsPercent = Math.min(100, Math.round((carbsVal / 100) * 100));
  const fatsPercent = Math.min(100, Math.round((fatsVal / 50) * 100));

  const isProteinMet = pVal >= targetProtein;
  const isCaloriesOver = cVal > maxCalories;

  const gauges = [
    {
      title: "Protein",
      val: pVal,
      suffix: "g",
      target: `${pVal}g / ${targetProtein}g Target`,
      percent: proteinPercent,
      textColor: isProteinMet ? "text-emerald-400" : "text-[#FC8019]",
      barColor: isProteinMet ? "bg-emerald-500" : "bg-[#FC8019]",
      icon: Dumbbell,
    },
    {
      title: "Calories",
      val: cVal,
      suffix: " kcal",
      target: `${cVal} / ${maxCalories} kcal`,
      percent: caloriesPercent,
      textColor: isCaloriesOver ? "text-red-400" : "text-zinc-200",
      barColor: isCaloriesOver ? "bg-red-500" : "bg-[#FC8019]",
      icon: Flame,
    },
    {
      title: "Carbs",
      val: carbsVal,
      suffix: "g",
      target: `${carbsVal}g • Est. Total`,
      percent: carbsPercent,
      textColor: "text-zinc-300",
      barColor: "bg-zinc-500",
      icon: Wheat,
    },
    {
      title: "Fats",
      val: fatsVal,
      suffix: "g",
      target: `${fatsVal}g • Est. Total`,
      percent: fatsPercent,
      textColor: "text-zinc-300",
      barColor: "bg-zinc-500",
      icon: Droplet,
    },
  ];

  return (
    <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-5 shadow-lg space-y-4">
      <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
        <BarChart3 className="w-4 h-4 text-[#FC8019]" />
        <span>Consolidated Macro Breakdown</span>
      </h3>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {gauges.map((g, idx) => {
          const Icon = g.icon;
          return (
            <div
              key={idx}
              className="p-3.5 rounded-xl bg-zinc-950/60 flex flex-col justify-between space-y-3"
            >
              <div className="flex items-center justify-between">
                <span className={`text-xs font-bold ${g.textColor} flex items-center gap-1.5`}>
                  <Icon className="w-3.5 h-3.5" /> {g.title}
                </span>
                <span className="text-[10px] font-mono text-zinc-400 font-semibold">
                  {g.target}
                </span>
              </div>

              <div>
                <div className={`text-lg font-extrabold font-mono ${g.textColor} mb-1.5`}>
                  <NumberTicker value={g.val} suffix={g.suffix} />
                </div>
                {/* Progress Bar Container */}
                <div className="w-full h-1.5 bg-zinc-900 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${g.percent}%` }}
                    transition={{ duration: 0.7, ease: "easeOut" }}
                    className={`h-full ${g.barColor} rounded-full`}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
