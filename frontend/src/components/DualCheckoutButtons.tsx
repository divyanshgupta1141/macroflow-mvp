"use client";

import React from "react";
import { Utensils, ShoppingBag, ExternalLink } from "lucide-react";

interface DualCheckoutButtonsProps {
  foodCartId?: string;
  instamartCartId?: string;
}

export const DualCheckoutButtons: React.FC<DualCheckoutButtonsProps> = ({
  foodCartId = "530602039",
  instamartCartId = "im_948201735",
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {/* Primary CTA: Swiggy Food Cart Link */}
      <a
        href={`https://swiggy.com/cart?cart_id=${foodCartId}`}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-between p-4 rounded-2xl bg-[#FC8019] hover:bg-[#e06f12] text-white font-semibold shadow-lg shadow-orange-500/20 transition-all cursor-pointer group"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-white/10 group-hover:bg-white/20 transition-colors">
            <Utensils className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-xs text-white/80 font-medium">Step 1 • Fleet 1</div>
            <div className="text-sm font-bold text-white">Checkout Food Cart</div>
          </div>
        </div>
        <ExternalLink className="w-4 h-4 text-white/80 group-hover:text-white transition-colors" />
      </a>

      {/* Secondary CTA: Swiggy Instamart Cart Link */}
      <a
        href={`https://swiggy.com/instamart/cart?cart_id=${instamartCartId}`}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center justify-between p-4 rounded-2xl bg-zinc-800 hover:bg-zinc-700 text-zinc-100 border border-zinc-700 transition-all cursor-pointer group"
      >
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-zinc-900 group-hover:bg-zinc-800 transition-colors">
            <ShoppingBag className="w-5 h-5 text-[#FC8019]" />
          </div>
          <div>
            <div className="text-xs text-zinc-400 font-medium">Step 2 • Fleet 2</div>
            <div className="text-sm font-bold text-zinc-100">Checkout Instamart Cart</div>
          </div>
        </div>
        <ExternalLink className="w-4 h-4 text-zinc-400 group-hover:text-zinc-200 transition-colors" />
      </a>
    </div>
  );
};
