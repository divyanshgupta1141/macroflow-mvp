"use client";

import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Utensils, TrendingDown, Dumbbell, Flame, Store, ShoppingBag } from "lucide-react";
import { DishImage } from "./DishImage";
import { NumberTicker } from "./ui/NumberTicker";
import { SyncTimelineBadge } from "./SyncTimelineBadge";

interface SplitCartDisplayProps {
  recommendation?: any;
  foodItem?: any;
  instamartItems?: any[];
  savings?: number;
  foodEta?: number;
  instamartEta?: number;
  isLoading?: boolean;
  isAlternative?: boolean;
}

export const SplitCartDisplay: React.FC<SplitCartDisplayProps> = ({
  recommendation,
  foodItem,
  instamartItems,
  savings = 225,
  foodEta = 32,
  instamartEta = 12,
  isLoading = false,
  isAlternative,
}) => {
  // 1. Restaurant Dish Data Binding (binds to recommendation.restaurant_dish)
  const dish = recommendation?.restaurant_dish || recommendation?.dish || foodItem || {};
  const dishName = dish?.name || "Selected Restaurant Dish";
  const restaurantName = dish?.restaurant || dish?.restaurant_name || "Swiggy Partner Restaurant";
  const dishPrice = dish?.price ?? dish?.final_price ?? 0;
  const dishProtein = dish?.protein ?? dish?.estimated_macros?.protein_g ?? 0;
  const dishCalories = dish?.calories ?? dish?.estimated_macros?.calories_kcal ?? 0;
  const dishDiet = dish?.diet || dish?.dietary_type || "NON_VEG";
  const isVeg = dishDiet === "VEG" || dishDiet === "VEGAN";
  const dishImage = dish?.image_url || dish?.imageUrl || "";

  // 2. Instamart Booster Data Binding (binds to recommendation.boosters)
  const boosters: any[] = recommendation?.boosters || recommendation?.instamart || instamartItems || [];
  const boostersTotal = boosters.reduce((sum: number, b: any) => sum + (b?.price ?? b?.final_price ?? 0), 0);
  const totalSavings = recommendation?.savings ?? savings;

  const showAlternativeBanner = isAlternative ?? recommendation?.is_alternative ?? false;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="space-y-4"
    >
      {/* Arbitrage Callout Banner & Delivery Timeline Sync Badge */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-stretch">
        <div className="md:col-span-2 bg-zinc-900/60 border border-zinc-800 rounded-2xl p-4 flex items-center justify-between gap-3 shadow-lg">
          <div className="flex items-center gap-3">
            <div className="h-8 w-8 rounded-lg bg-orange-500/10 text-[#FC8019] flex items-center justify-center shrink-0">
              <TrendingDown className="w-4 h-4" />
            </div>
            <div className="text-xs sm:text-sm font-extrabold text-zinc-100">
              Cross-Fleet Arbitrage:{" "}
              <span className="text-[#FC8019]">
                Saved <NumberTicker value={totalSavings} prefix="₹" />
              </span>{" "}
              vs ordering single restaurant meals
            </div>
          </div>
        </div>

        <div className="md:col-span-1">
          <SyncTimelineBadge instamartMins={instamartEta} foodMins={foodEta} />
        </div>
      </div>

      {/* Dual Fleet Cards with AnimatePresence layout morph */}
      <AnimatePresence mode="wait">
        {isLoading ? (
          <motion.div
            key="skeleton"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            transition={{ duration: 0.2 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            <div className="w-full rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-5 backdrop-blur-md">
              <div className="flex items-center gap-4">
                <div className="h-20 w-20 animate-pulse rounded-xl bg-zinc-800" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-3/4 animate-pulse rounded bg-zinc-800" />
                  <div className="h-3 w-1/2 animate-pulse rounded bg-zinc-800/60" />
                  <div className="flex gap-2 pt-1">
                    <div className="h-5 w-16 animate-pulse rounded-full bg-zinc-800" />
                    <div className="h-5 w-16 animate-pulse rounded-full bg-zinc-800" />
                  </div>
                </div>
              </div>
            </div>

            <div className="w-full rounded-2xl border border-zinc-800/80 bg-zinc-900/50 p-5 backdrop-blur-md">
              <div className="flex items-center gap-4">
                <div className="h-20 w-20 animate-pulse rounded-xl bg-zinc-800" />
                <div className="flex-1 space-y-2">
                  <div className="h-4 w-3/4 animate-pulse rounded bg-zinc-800" />
                  <div className="h-3 w-1/2 animate-pulse rounded bg-zinc-800/60" />
                </div>
              </div>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key={dish.id || "dish-card"}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className="grid grid-cols-1 md:grid-cols-2 gap-4"
          >
            {/* Fleet 1: Swiggy Food */}
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-4 flex flex-col justify-between space-y-3">
              <div>
                {/* Alternative Query Banner */}
                {showAlternativeBanner && (
                  <div className="mb-3 inline-flex items-center gap-1.5 rounded-md bg-amber-500/10 px-2.5 py-1 text-xs text-amber-300 border border-amber-500/20 w-full">
                    <span>Requested outlet unavailable nearby - showing highest protein alternative in Rudrapur</span>
                  </div>
                )}

                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2 font-bold text-xs text-[#FC8019] uppercase tracking-wider">
                    <Utensils className="w-4 h-4" />
                    <span>Fleet 1 • Swiggy Food</span>
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-wider bg-orange-500/10 text-[#FC8019] px-2.5 py-0.5 rounded-full">
                    {dishDiet}
                  </span>
                </div>

                <div className="flex gap-3">
                  <div className="w-32 h-24 shrink-0 rounded-xl overflow-hidden bg-zinc-950">
                    <DishImage
                      src={dishImage}
                      alt={dishName}
                      dishName={dishName}
                      isVeg={isVeg}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div className="space-y-1.5 min-w-0 flex-1">
                    <h3 className="text-sm font-bold text-zinc-100 line-clamp-2 leading-snug">
                      {dishName}
                    </h3>
                    <div className="flex items-center gap-1.5 text-xs text-zinc-400">
                      <Store className="w-3.5 h-3.5 text-zinc-500" />
                      <span className="truncate">{restaurantName}</span>
                    </div>
                    <div className="flex items-center gap-2 pt-0.5">
                      <span className="text-[11px] font-bold text-[#FC8019] bg-orange-500/10 px-2 py-0.5 rounded flex items-center gap-1">
                        <Dumbbell className="w-3 h-3" />
                        <NumberTicker value={dishProtein} suffix="g Protein" />
                      </span>
                      <span className="text-[11px] font-semibold text-zinc-400 flex items-center gap-1">
                        <Flame className="w-3 h-3 text-[#FC8019]" />
                        <NumberTicker value={dishCalories} suffix=" kcal" />
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-2.5 border-t border-zinc-800/60 text-xs font-bold">
                <span className="text-zinc-400">Dish Price</span>
                <span className="text-zinc-100 font-mono text-sm">
                  <NumberTicker value={dishPrice} prefix="₹" />
                </span>
              </div>
            </div>

            {/* Fleet 2: Swiggy Instamart */}
            <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-4 flex flex-col justify-between space-y-3">
              <div>
                <div className="flex items-center justify-between mb-3">
                  <div className="inline-flex items-center gap-1.5 bg-zinc-950 border border-zinc-800 rounded-full px-3 py-1 text-xs text-zinc-300 font-extrabold">
                    <span className="w-2 h-2 rounded-full bg-[#FC8019] animate-pulse" />
                    <span>INSTAMART 10-MIN GROCERY</span>
                  </div>
                </div>

                {/* Instamart Item List / Empty State */}
                <div className="space-y-2">
                  {boosters.length === 0 ? (
                    <div className="p-4 rounded-xl bg-zinc-950/60 border border-zinc-800/60 text-center space-y-1 my-2">
                      <div className="flex justify-center text-zinc-500 mb-1">
                        <ShoppingBag className="w-5 h-5 text-zinc-600" />
                      </div>
                      <div className="text-xs font-semibold text-zinc-300">
                        No Instamart boosters required
                      </div>
                      <div className="text-[11px] text-zinc-500">
                        Standalone base dish satisfies budget constraints
                      </div>
                    </div>
                  ) : (
                    boosters.map((b: any, idx: number) => {
                      const bName = b?.name || "Instamart Booster";
                      const bPrice = b?.price ?? b?.final_price ?? 0;
                      const bProtein = b?.protein ?? b?.estimated_macros?.protein_g ?? 0;
                      const bCalories = b?.calories ?? b?.estimated_macros?.calories_kcal ?? 0;
                      const bImg = b?.image_url || b?.imageUrl || "";
                      const bIsVeg = b?.is_veg ?? true;

                      return (
                        <div
                          key={b.sku_id || b.item_id || idx}
                          className="flex items-center justify-between p-2 rounded-xl bg-zinc-950/60 border border-zinc-800/60"
                        >
                          <div className="flex items-center gap-3 min-w-0">
                            <div className="w-10 h-10 rounded-lg overflow-hidden shrink-0">
                              <DishImage
                                src={bImg}
                                alt={bName}
                                dishName={bName}
                                isVeg={bIsVeg}
                                className="w-full h-full object-cover"
                              />
                            </div>
                            <div className="min-w-0">
                              <div className="text-xs font-bold text-zinc-200 truncate">{bName}</div>
                              <div className="text-[11px] text-zinc-400 flex items-center gap-1.5 mt-0.5">
                                <span className="text-[#FC8019] font-bold">
                                  +<NumberTicker value={bProtein} suffix="g Protein" />
                                </span>
                                <span className="text-zinc-600">•</span>
                                <span>
                                  <NumberTicker value={bCalories} suffix=" kcal" />
                                </span>
                              </div>
                            </div>
                          </div>
                          <span className="text-xs font-mono font-bold text-zinc-200 ml-2 shrink-0">
                            <NumberTicker value={bPrice} prefix="₹" />
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>
              </div>

              <div className="flex justify-between items-center pt-2.5 border-t border-zinc-800/60 text-xs font-bold">
                <span className="text-zinc-400">Boosters Total</span>
                <span className="text-zinc-100 font-mono text-sm">
                  <NumberTicker value={boostersTotal} prefix="₹" />
                </span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};
