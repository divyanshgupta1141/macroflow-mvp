import React from "react";
import { Zap } from "lucide-react";

interface InstamartBadgeProps {
  className?: string;
  size?: "sm" | "md";
}

export const InstamartBadge: React.FC<InstamartBadgeProps> = ({
  className = "",
  size = "md",
}) => {
  return (
    <div
      className={`inline-flex items-center gap-1.5 bg-zinc-900 border border-[#FC8019]/40 shadow-lg shadow-orange-500/10 rounded-full text-zinc-100 font-extrabold ${
        size === "sm" ? "px-2.5 py-0.5 text-[10px]" : "px-3 py-1 text-xs"
      } ${className}`}
    >
      <div className="bg-orange-500/20 text-[#FC8019] p-0.5 rounded-full border border-orange-500/40">
        <Zap className={size === "sm" ? "w-2.5 h-2.5" : "w-3.5 h-3.5"} />
      </div>
      <span className="tracking-wide">
        INSTAMART <span className="text-[#FC8019] font-black">10-MIN GROCERY</span>
      </span>
    </div>
  );
};
