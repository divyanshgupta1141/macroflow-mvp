"use client";

import React, { useState } from "react";
import { Utensils, Flame, Salad, Soup, Egg } from "lucide-react";

interface DishImageProps {
  src?: string;
  alt: string;
  dishName: string;
  isVeg?: boolean;
  className?: string;
}

export const DishImage: React.FC<DishImageProps> = ({
  src,
  alt,
  dishName,
  isVeg = false,
  className = "w-full h-full object-cover",
}) => {
  const [hasError, setHasError] = useState(false);

  const isInvalidUrl =
    !src ||
    src.includes("placeholder") ||
    (!src.startsWith("http://") && !src.startsWith("https://"));

  if (!hasError && !isInvalidUrl && src) {
    return (
      <img
        src={src}
        alt={alt}
        className={className}
        onError={() => setHasError(true)}
      />
    );
  }

  // Fallback Cuisine Icon & Dietary Badge Card
  const lowerName = (dishName || "").toLowerCase();
  let IconComponent = Utensils;
  let iconColorClass = "text-[#FC8019]";

  if (lowerName.includes("soup")) {
    IconComponent = Soup;
    iconColorClass = "text-amber-400";
  } else if (
    lowerName.includes("salad") ||
    lowerName.includes("vegan") ||
    lowerName.includes("green")
  ) {
    IconComponent = Salad;
    iconColorClass = "text-emerald-400";
  } else if (
    lowerName.includes("flame") ||
    lowerName.includes("tikka") ||
    lowerName.includes("tandoori") ||
    lowerName.includes("kebab") ||
    lowerName.includes("peri")
  ) {
    IconComponent = Flame;
    iconColorClass = "text-orange-500";
  } else if (lowerName.includes("egg") || lowerName.includes("omelette")) {
    IconComponent = Egg;
    iconColorClass = "text-yellow-400";
  }

  const abbr = dishName
    ? dishName
        .split(" ")
        .map((w) => w[0])
        .filter(Boolean)
        .slice(0, 3)
        .join("")
        .toUpperCase()
    : "DISH";

  return (
    <div className="w-full h-full min-h-[80px] bg-zinc-950 border border-zinc-800 rounded-xl p-2 flex flex-col items-center justify-center gap-1.5 relative overflow-hidden select-none">
      <div className="flex items-center gap-1 absolute top-1.5 right-1.5">
        <span
          className={`w-2 h-2 rounded-full ${
            isVeg
              ? "bg-emerald-500 shadow-sm shadow-emerald-500/50"
              : "bg-red-500 shadow-sm shadow-red-500/50"
          }`}
          title={isVeg ? "Vegetarian" : "Non-Vegetarian"}
        />
      </div>

      <div className="p-2 rounded-full bg-zinc-900 border border-zinc-800">
        <IconComponent className={`w-5 h-5 ${iconColorClass}`} />
      </div>

      <span className="text-[10px] font-bold text-zinc-300 tracking-wide text-center truncate max-w-full px-1">
        {abbr}
      </span>
    </div>
  );
};
