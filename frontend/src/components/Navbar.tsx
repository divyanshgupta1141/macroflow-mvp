"use client";

import React from "react";
import { MapPin, Terminal } from "lucide-react";
import { MacroFlowLogo } from "./MacroFlowLogo";

interface Address {
  addressId: string;
  label: string;
  addressString: string;
}

interface NavbarProps {
  addresses: Address[];
  selectedAddressId: string;
  setSelectedAddressId: (id: string) => void;
  onToggleDevDrawer: () => void;
  isDevDrawerOpen: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({
  addresses,
  selectedAddressId,
  setSelectedAddressId,
  onToggleDevDrawer,
}) => {
  return (
    <header className="sticky top-0 z-40 w-full bg-[#090D14]/90 backdrop-blur-md border-b border-zinc-800/80 px-4 sm:px-8 py-3 transition-all" suppressHydrationWarning>
      <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
        {/* MacroFlow AI Logo */}
        <div className="flex items-center">
          <MacroFlowLogo className="h-8 w-auto" />
        </div>

        {/* Right Section: Address Selector & Developer MCP Terminal Toggle */}
        <div className="flex items-center gap-3">
          {/* Active Delivery Address Dropdown */}
          <div className="flex items-center gap-2 bg-zinc-900 border border-zinc-800 rounded-xl px-3 py-1.5 text-xs text-zinc-300">
            <MapPin className="w-4 h-4 text-[#FC8019] shrink-0" />
            <select
              id="selected-address-dropdown"
              name="selected_address_dropdown"
              data-m-id="selected_address_dropdown"
              suppressHydrationWarning
              value={selectedAddressId}
              onChange={(e) => setSelectedAddressId(e.target.value)}
              className="bg-transparent text-zinc-200 font-medium focus:outline-none cursor-pointer max-w-[180px] sm:max-w-[240px] truncate"
            >
              {addresses.map((addr) => (
                <option key={addr.addressId} value={addr.addressId} className="bg-zinc-900 text-zinc-200">
                  {addr.label || "Address"} ({addr.addressString || addr.addressId})
                </option>
              ))}
            </select>
          </div>

          {/* Discreet Developer MCP Terminal Slide-Over Button */}
          <button
            type="button"
            onClick={onToggleDevDrawer}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-zinc-800/60 hover:bg-zinc-700/60 border border-zinc-700/50 text-xs font-mono text-zinc-400 hover:text-zinc-200 transition-colors cursor-pointer"
            title="Toggle Developer MCP Logs & Environment Drawer"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">MCP Logs</span>
            <span className="w-1.5 h-1.5 rounded-full bg-[#FC8019] animate-pulse" />
          </button>
        </div>
      </div>
    </header>
  );
};
