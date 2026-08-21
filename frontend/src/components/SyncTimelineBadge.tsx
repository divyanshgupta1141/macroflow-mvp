"use client";

import React from "react";
import { Clock, Zap, Bike } from "lucide-react";

interface SyncTimelineProps {
  instamartMins?: number;
  foodMins?: number;
}

export function SyncTimelineBadge({
  instamartMins = 12,
  foodMins = 32,
}: SyncTimelineProps) {
  return (
    <div className="flex flex-col gap-2 rounded-xl border border-zinc-800/80 bg-gradient-to-r from-zinc-900/90 via-zinc-900/50 to-zinc-900/90 p-3.5 backdrop-blur-md">
      <div className="flex items-center justify-between text-xs text-zinc-400">
        <div className="flex items-center gap-1.5 font-medium text-zinc-200">
          <Clock className="h-3.5 w-3.5 text-amber-400" />
          <span>Cross-Fleet Delivery Sync</span>
        </div>
        <span className="text-[11px] text-zinc-500 font-mono">Parallel Dispatch</span>
      </div>

      <div className="grid grid-cols-2 gap-3 pt-1">
        {/* Fleet 1: Instamart */}
        <div className="flex items-center gap-2.5 rounded-lg bg-zinc-950/60 p-2 border border-zinc-800/40">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-amber-500/10 text-amber-400">
            <Zap className="h-4 w-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Instamart</div>
            <div className="text-xs font-semibold text-zinc-200">{instamartMins} mins</div>
          </div>
        </div>

        {/* Fleet 2: Food Delivery */}
        <div className="flex items-center gap-2.5 rounded-lg bg-zinc-950/60 p-2 border border-zinc-800/40">
          <div className="flex h-7 w-7 items-center justify-center rounded-md bg-orange-500/10 text-orange-400">
            <Bike className="h-4 w-4" />
          </div>
          <div>
            <div className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Restaurant</div>
            <div className="text-xs font-semibold text-zinc-200">{foodMins} mins</div>
          </div>
        </div>
      </div>
    </div>
  );
}
