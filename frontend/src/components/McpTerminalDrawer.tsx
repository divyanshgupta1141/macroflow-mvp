"use client";

import React from "react";
import { Terminal, X, Code, CheckCircle, Zap, Layers } from "lucide-react";

interface TraceStep {
  type?: string;
  name?: string;
  tool?: string;
  args?: any;
  payload?: any;
  status?: string;
  [key: string]: any;
}

interface McpTerminalDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  executionMode: "sandbox" | "live_mcp";
  isMcpTokenActive: boolean;
  onSelectMode: (mode: "sandbox" | "live_mcp") => void;
  traceSteps: TraceStep[];
}

export const McpTerminalDrawer: React.FC<McpTerminalDrawerProps> = ({
  isOpen,
  onClose,
  executionMode,
  isMcpTokenActive,
  onSelectMode,
  traceSteps,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-black/60 backdrop-blur-sm flex justify-end">
      {/* Slide-over Sheet Container */}
      <div className="w-full max-w-md bg-zinc-950 border-l border-zinc-800 h-full flex flex-col shadow-2xl animate-in slide-in-from-right duration-200">
        {/* Drawer Header */}
        <div className="p-4 border-b border-zinc-800 flex items-center justify-between bg-zinc-900/80">
          <div className="flex items-center gap-2 font-mono text-xs font-bold text-zinc-100">
            <Terminal className="w-4 h-4 text-[#FC8019]" />
            <span>Developer MCP Logs & Settings</span>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-zinc-800 text-zinc-400 hover:text-white transition-colors cursor-pointer"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Internal Testing Execution Mode Toggle */}
        <div className="p-4 bg-zinc-900/40 border-b border-zinc-800/80 space-y-2">
          <div className="text-[11px] font-mono font-semibold text-zinc-400 uppercase tracking-wider">
            Environment & Mode Control
          </div>
          <div className="grid grid-cols-2 gap-2 bg-zinc-950 p-1 rounded-xl border border-zinc-800 text-xs font-mono font-medium">
            <button
              onClick={() => onSelectMode("sandbox")}
              className={`flex items-center justify-center gap-1.5 py-1.5 rounded-lg transition-all cursor-pointer ${
                executionMode === "sandbox"
                  ? "bg-zinc-800 text-white font-bold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Layers className="w-3.5 h-3.5" /> Sandbox Mode
            </button>
            <button
              onClick={() => onSelectMode("live_mcp")}
              className={`flex items-center justify-center gap-1.5 py-1.5 rounded-lg transition-all cursor-pointer ${
                executionMode === "live_mcp"
                  ? isMcpTokenActive
                    ? "bg-orange-500/20 text-[#FC8019] font-bold"
                    : "bg-orange-500/20 text-[#FC8019] font-bold"
                  : "text-zinc-400 hover:text-zinc-200"
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-[#FC8019]" /> Live MCP OAuth
            </button>
          </div>
        </div>

        {/* Execution Trace Terminal Body */}
        <div className="flex-1 overflow-y-auto p-4 space-y-3 font-mono text-xs text-zinc-300">
          <div className="text-[11px] font-semibold text-zinc-400 uppercase tracking-wider mb-2">
            Tool Call Event Stream ({traceSteps.length})
          </div>

          {traceSteps.length === 0 ? (
            <div className="text-zinc-500 italic py-4 text-center">
              No tool trace events recorded yet. Run a prompt to view MCP execution logs.
            </div>
          ) : (
            traceSteps.map((step, idx) => (
              <div
                key={idx}
                className="p-3 rounded-xl bg-zinc-900/80 border border-zinc-800 space-y-1.5"
              >
                <div className="flex items-center justify-between text-zinc-400 font-semibold">
                  <span className="flex items-center gap-1.5 text-[#FC8019]">
                    <Code className="w-3.5 h-3.5" /> [{idx + 1}] {step.tool || step.name || "Tool Event"}
                  </span>
                  <span className="inline-flex items-center gap-1 text-[10px] text-[#FC8019] bg-orange-500/10 px-2 py-0.5 rounded font-bold">
                    <CheckCircle className="w-3 h-3" /> {step.status || "EXECUTED"}
                  </span>
                </div>

                <pre className="p-2.5 rounded-lg bg-zinc-950 border border-zinc-900 overflow-x-auto text-[11px] text-zinc-300 leading-relaxed">
                  {JSON.stringify(step, null, 2)}
                </pre>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
