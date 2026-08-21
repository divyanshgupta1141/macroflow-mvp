"use client";

import React from "react";
import { motion } from "framer-motion";
import { SlidersHorizontal, RotateCcw } from "lucide-react";

export type DietaryType = "ALL" | "NON_VEG" | "VEG" | "EGGETARIAN" | "VEGAN";

interface SidebarFiltersProps {
  dietaryPreference: DietaryType;
  setDietaryPreference: (diet: DietaryType) => void;
  targetProtein: number;
  setTargetProtein: (p: number) => void;
  maxCalories: number;
  setMaxCalories: (c: number) => void;
  maxBudget: number;
  setMaxBudget: (b: number) => void;
  onResetHistory: () => void;
}

export const SidebarFilters: React.FC<SidebarFiltersProps> = ({
  dietaryPreference,
  setDietaryPreference,
  targetProtein,
  setTargetProtein,
  maxCalories,
  setMaxCalories,
  maxBudget,
  setMaxBudget,
  onResetHistory,
}) => {
  const dietaryOptions: { label: string; value: DietaryType }[] = [
    { label: "All", value: "ALL" },
    { label: "Non-Veg", value: "NON_VEG" },
    { label: "Veg", value: "VEG" },
    { label: "Egg", value: "EGGETARIAN" },
    { label: "Vegan", value: "VEGAN" },
  ];

  const handlePreset = (p: number, c: number, b: number) => {
    setTargetProtein(p);
    setMaxCalories(c);
    setMaxBudget(b);
  };

  return (
    <aside className="w-full lg:w-80 shrink-0 sticky top-20 self-start bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-5 shadow-lg space-y-6" suppressHydrationWarning>
      {/* Dietary Preference Selector with Framer Motion Sliding Pill */}
      <div suppressHydrationWarning>
        <h2 className="text-sm font-bold text-zinc-100 mb-1 flex items-center gap-2">
          <SlidersHorizontal className="w-4 h-4 text-[#FC8019]" /> Dietary Preference
        </h2>
        <p className="text-[11px] text-zinc-400 mb-3">Filter restaurant and Instamart options</p>
        <div className="grid grid-cols-3 gap-1.5 bg-zinc-950/80 p-1.5 rounded-xl relative">
          {dietaryOptions.map((opt) => {
            const isSelected = dietaryPreference === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => setDietaryPreference(opt.value)}
                className="relative py-1.5 px-2 rounded-lg text-xs font-semibold transition-colors cursor-pointer text-center z-10"
              >
                {isSelected && (
                  <motion.div
                    layoutId="dietPill"
                    className="absolute inset-0 bg-[#FC8019] rounded-lg -z-10 shadow-md shadow-orange-500/20"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
                <span className={isSelected ? "text-white font-semibold" : "text-zinc-400 hover:text-zinc-200"}>
                  {opt.label}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      <hr className="border-zinc-800/60" />

      {/* Target Sliders with Unified Swiggy Orange Track Accents */}
      <div className="space-y-4" suppressHydrationWarning>
        <h2 className="text-sm font-bold text-zinc-100 mb-1">
          Target Constraints
        </h2>

        {/* Protein Slider */}
        <div className="space-y-1.5" suppressHydrationWarning>
          <div className="flex justify-between text-xs font-medium">
            <span className="text-zinc-300 font-semibold">Target Protein</span>
            <span className="font-mono text-[#FC8019] bg-orange-500/10 px-2 py-0.5 rounded font-bold">
              {targetProtein}g+
            </span>
          </div>
          <input
            id="target-protein-slider"
            name="target_protein_slider"
            type="range"
            min={10}
            max={120}
            step={5}
            value={targetProtein}
            onChange={(e) => setTargetProtein(Number(e.target.value))}
            autoComplete="off"
            data-m-id="target_protein_slider"
            suppressHydrationWarning
            className="w-full accent-[#FC8019] bg-zinc-800 rounded-lg h-1.5 cursor-pointer"
          />
        </div>

        {/* Calories Slider */}
        <div className="space-y-1.5" suppressHydrationWarning>
          <div className="flex justify-between text-xs font-medium">
            <span className="text-zinc-300 font-semibold">Max Calories</span>
            <span className="font-mono text-zinc-200 bg-zinc-800 px-2 py-0.5 rounded font-bold">
              &lt;{maxCalories} kcal
            </span>
          </div>
          <input
            id="max-calories-slider"
            name="max_calories_slider"
            type="range"
            min={200}
            max={1500}
            step={50}
            value={maxCalories}
            onChange={(e) => setMaxCalories(Number(e.target.value))}
            autoComplete="off"
            data-m-id="max_calories_slider"
            suppressHydrationWarning
            className="w-full accent-[#FC8019] bg-zinc-800 rounded-lg h-1.5 cursor-pointer"
          />
        </div>

        {/* Budget Slider */}
        <div className="space-y-1.5" suppressHydrationWarning>
          <div className="flex justify-between text-xs font-medium">
            <span className="text-zinc-300 font-semibold">Max Budget</span>
            <span className="font-mono text-zinc-200 bg-zinc-800 px-2 py-0.5 rounded font-bold">
              &lt;₹{maxBudget}
            </span>
          </div>
          <input
            id="max-budget-slider"
            name="max_budget_slider"
            type="range"
            min={150}
            max={2000}
            step={50}
            value={maxBudget}
            onChange={(e) => setMaxBudget(Number(e.target.value))}
            autoComplete="off"
            data-m-id="max_budget_slider"
            suppressHydrationWarning
            className="w-full accent-[#FC8019] bg-zinc-800 rounded-lg h-1.5 cursor-pointer"
          />
        </div>
      </div>

      <hr className="border-zinc-800/60" />

      {/* Quick Presets */}
      <div>
        <h3 className="text-[11px] font-bold text-zinc-400 uppercase tracking-wider mb-2.5">
          Quick Presets
        </h3>
        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            onClick={() => handlePreset(50, 650, 450)}
            className="flex flex-col items-center justify-center p-2 rounded-xl bg-zinc-950 hover:bg-zinc-800 text-xs font-semibold text-zinc-300 hover:text-white transition-all cursor-pointer"
          >
            <span className="text-[#FC8019] font-bold">50g</span>
            <span className="text-[10px] text-zinc-400">Gym</span>
          </button>
          <button
            type="button"
            onClick={() => handlePreset(35, 480, 320)}
            className="flex flex-col items-center justify-center p-2 rounded-xl bg-zinc-950 hover:bg-zinc-800 text-xs font-semibold text-zinc-300 hover:text-white transition-all cursor-pointer"
          >
            <span className="text-zinc-200 font-bold">35g</span>
            <span className="text-[10px] text-zinc-400">Lean</span>
          </button>
          <button
            type="button"
            onClick={() => handlePreset(45, 600, 400)}
            className="flex flex-col items-center justify-center p-2 rounded-xl bg-zinc-950 hover:bg-zinc-800 text-xs font-semibold text-zinc-300 hover:text-white transition-all cursor-pointer"
          >
            <span className="text-[#FC8019] font-bold">45g</span>
            <span className="text-[10px] text-zinc-400">Keto</span>
          </button>
        </div>
      </div>

      <hr className="border-zinc-800/60" />

      {/* Clear History Button */}
      <button
        type="button"
        onClick={onResetHistory}
        className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-zinc-950 hover:bg-zinc-800 text-xs font-semibold text-zinc-400 hover:text-white transition-all cursor-pointer"
      >
        <RotateCcw className="w-3.5 h-3.5" /> Clear History
      </button>
    </aside>
  );
};
