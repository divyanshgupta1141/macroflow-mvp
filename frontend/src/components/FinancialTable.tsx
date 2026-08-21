"use client";

import React from "react";
import { Receipt, Truck, CheckCircle2, ShieldCheck } from "lucide-react";

interface FinancialTableProps {
  recommendation?: any;
  itemsSubtotal?: number;
  foodDeliveryFee?: number;
  instamartDeliveryFee?: number;
  taxesFees?: number;
  totalPayable?: number;
  maxBudget?: number;
}

export const FinancialTable: React.FC<FinancialTableProps> = ({
  recommendation,
  itemsSubtotal = 0,
  foodDeliveryFee = 35,
  instamartDeliveryFee = 15,
  taxesFees = 25,
  totalPayable = 0,
  maxBudget = 400,
}) => {
  const subtotal = recommendation?.subtotal ?? itemsSubtotal;
  const foodFee = recommendation?.food_fee ?? foodDeliveryFee;
  const imFee = recommendation?.instamart_fee ?? (recommendation?.boosters && recommendation.boosters.length > 0 ? 15 : instamartDeliveryFee);
  const taxes = recommendation?.taxes_platform ?? taxesFees;
  const total = recommendation?.total_payable ?? recommendation?.cost ?? totalPayable;

  const isUnderBudget = total <= maxBudget;
  const isWithinTolerance = total <= maxBudget + 15;

  return (
    <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-5 shadow-lg space-y-4">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
        <h3 className="text-sm font-bold text-zinc-100 flex items-center gap-2">
          <Receipt className="w-4 h-4 text-[#FC8019]" />
          <span>Financial & Fee Accounting</span>
        </h3>
        <span
          className={`inline-flex items-center gap-1 text-xs font-bold px-3 py-1 rounded-full ${
            isUnderBudget
              ? "bg-zinc-800 text-zinc-200"
              : isWithinTolerance
              ? "bg-zinc-800 text-amber-400"
              : "bg-zinc-800 text-zinc-300"
          }`}
        >
          {isUnderBudget ? (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-zinc-400" /> Under Budget (&lt;₹{maxBudget})
            </>
          ) : isWithinTolerance ? (
            <>
              <ShieldCheck className="w-3.5 h-3.5 text-amber-400" /> Within Feasible Tolerance (₹{total} total including fees)
            </>
          ) : (
            <>
              <ShieldCheck className="w-3.5 h-3.5 text-zinc-400" /> Total: ₹{total} (inc fees)
            </>
          )}
        </span>
      </div>

      {/* Flat elevation grid without heavy inner borders */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 text-xs">
        <div className="p-3 rounded-xl bg-zinc-950/60">
          <div className="text-zinc-400 font-medium mb-1">Subtotal</div>
          <div className="text-sm font-bold font-mono text-zinc-200">₹{subtotal}</div>
        </div>

        <div className="p-3 rounded-xl bg-zinc-950/60">
          <div className="text-zinc-400 font-medium mb-1 flex items-center gap-1">
            <Truck className="w-3 h-3 text-[#FC8019]" /> Food Fee
          </div>
          <div className="text-sm font-bold font-mono text-zinc-200">₹{foodFee}</div>
        </div>

        <div className="p-3 rounded-xl bg-zinc-950/60">
          <div className="text-zinc-400 font-medium mb-1 flex items-center gap-1">
            <Truck className="w-3 h-3 text-zinc-400" /> Instamart Fee
          </div>
          <div className="text-sm font-bold font-mono text-zinc-200">₹{imFee}</div>
        </div>

        <div className="p-3 rounded-xl bg-zinc-950/60">
          <div className="text-zinc-400 font-medium mb-1">Taxes & Platform</div>
          <div className="text-sm font-bold font-mono text-zinc-200">₹{taxes}</div>
        </div>

        <div className="col-span-2 sm:col-span-1 p-3 rounded-xl bg-zinc-800/80 flex flex-col justify-center border border-zinc-700/50">
          <div className="text-zinc-300 font-bold mb-0.5">Total Payable</div>
          <div className="text-lg font-extrabold font-mono text-white">₹{total}</div>
        </div>
      </div>
    </div>
  );
};
