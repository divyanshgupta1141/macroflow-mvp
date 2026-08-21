import React from "react";

export const MacroFlowLogo = ({ className = "h-8" }: { className?: string }) => (
  <div className={`flex items-center gap-2.5 ${className}`}>
    {/* Swiggy Orange #FC8019 Logo Icon */}
    <div className="relative w-8 h-8 rounded-xl bg-[#FC8019] p-0.5 shadow-lg shadow-orange-500/20 flex items-center justify-center shrink-0">
      <svg
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        className="w-5 h-5 text-white"
      >
        <path
          d="M4 18V6L10 13L14 8.5L20 18M4 18H20"
          stroke="currentColor"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle cx="4" cy="6" r="1.5" fill="currentColor" />
        <circle cx="10" cy="13" r="1.5" fill="currentColor" />
        <circle cx="14" cy="8.5" r="1.5" fill="currentColor" />
        <circle cx="20" cy="18" r="1.5" fill="currentColor" />
      </svg>
    </div>
    <div className="flex flex-col">
      <div className="flex items-center gap-2">
        <span className="font-extrabold text-xl tracking-tight text-white leading-none">
          MacroFlow
        </span>
        <span className="text-[9px] font-mono font-bold uppercase tracking-widest text-zinc-400 bg-zinc-800/90 border border-zinc-700/60 px-2 py-0.5 rounded-full">
          MCP Gateway • v2024-11-05
        </span>
      </div>
    </div>
  </div>
);
