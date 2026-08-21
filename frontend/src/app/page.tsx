"use client";

import React, { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { SidebarFilters, DietaryType } from "@/components/SidebarFilters";
import { SplitCartDisplay } from "@/components/SplitCartDisplay";
import { MacroGauges } from "@/components/MacroGauges";
import { FinancialTable } from "@/components/FinancialTable";
import { DualCheckoutButtons } from "@/components/DualCheckoutButtons";
import { ParetoCard } from "@/components/ParetoCard";
import { McpTerminalDrawer } from "@/components/McpTerminalDrawer";
import { Search, Loader2, Zap, Link2 } from "lucide-react";

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000").replace(/\/+$/, "");

interface Address {
  addressId: string;
  label: string;
  addressString: string;
}

export default function Home() {
  const [executionMode, setExecutionMode] = useState<"sandbox" | "live_mcp">("sandbox");
  const [isMcpTokenActive, setIsMcpTokenActive] = useState<boolean>(false);
  const [showOAuthModal, setShowOAuthModal] = useState<boolean>(false);
  const [isDevDrawerOpen, setIsDevDrawerOpen] = useState<boolean>(false);

  const [dietaryPreference, setDietaryPreference] = useState<DietaryType>("ALL");
  const [addresses, setAddresses] = useState<Address[]>([
    { addressId: "ctvea5srb5vobit8qosg", label: "Home", addressString: "Indiranagar, Bengaluru" },
    { addressId: "work_addr_987", label: "Work", addressString: "Koramangala, Bengaluru" }
  ]);
  const [selectedAddressId, setSelectedAddressId] = useState<string>("ctvea5srb5vobit8qosg");

  const [targetProtein, setTargetProtein] = useState<number>(60);
  const [maxCalories, setMaxCalories] = useState<number>(650);
  const [maxBudget, setMaxBudget] = useState<number>(400);

  const [userQuery, setUserQuery] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [selectedParetoOption, setSelectedParetoOption] = useState<"A" | "B">("A");
  const [apiData, setApiData] = useState<any>(null);

  const [traceSteps, setTraceSteps] = useState<any[]>([
    { tool: "get_user_addresses", status: "SUCCESS", payload: { address_id: "ctvea5srb5vobit8qosg" } },
    { tool: "parallel_catalog_discovery", status: "SUCCESS", payload: { dishes_found: 3, skus_found: 4 } },
    { tool: "cross_fleet_knapsack_optimizer", status: "SUCCESS", payload: { selected_protein: 61, total_payable: 440 } },
    { tool: "create_dual_fleet_cart", status: "SUCCESS", payload: { food_cart_id: "530602039", instamart_cart_id: "im_948201735" } }
  ]);

  const [hybridState, setHybridState] = useState<any>(null);

  const checkMcpToken = async (): Promise<boolean> => {
    try {
      const res = await fetch(`${API_BASE_URL}/token`);
      if (res.ok) {
        const data = await res.json();
        if (data.authenticated || data.token || data.access_token) {
          setIsMcpTokenActive(true);
          setShowOAuthModal(false);
          return true;
        }
      }
    } catch (err) {
      console.warn("Token check failed:", err);
    }
    setIsMcpTokenActive(false);
    return false;
  };

  const handleSelectMode = async (mode: "sandbox" | "live_mcp") => {
    setExecutionMode(mode);
    if (mode === "live_mcp") {
      const active = await checkMcpToken();
      if (!active) {
        setShowOAuthModal(true);
      }
    } else {
      setShowOAuthModal(false);
    }
  };

  const handleStartOAuth = () => {
    const width = 500;
    const height = 650;
    const left = window.screen.width / 2 - width / 2;
    const top = window.screen.height / 2 - height / 2;

    const authWindow = window.open(
      `${API_BASE_URL}/login`,
      "SwiggyAuth",
      `width=${width},height=${height},top=${top},left=${left}`
    );

    const interval = setInterval(async () => {
      const active = await checkMcpToken();
      if (active) {
        clearInterval(interval);
        if (authWindow && !authWindow.closed) {
          authWindow.close();
        }
      }
    }, 1000);
  };

  const handleOptimize = async (
    customPrompt?: string,
    customAddressId?: string,
    customDiet?: DietaryType,
    customProtein?: number,
    customCalories?: number,
    customBudget?: number
  ) => {
    const addrId = customAddressId || selectedAddressId;
    const dietToUse = customDiet || dietaryPreference;
    const proteinToUse = customProtein ?? targetProtein;
    const caloriesToUse = customCalories ?? maxCalories;
    const budgetToUse = customBudget ?? maxBudget;

    const dietPrefix = dietToUse !== "ALL" ? `${dietToUse} ` : "";
    const promptToUse = customPrompt || userQuery || `${dietPrefix}${proteinToUse}g protein under ₹${budgetToUse} and <${caloriesToUse} kcal`;
    setIsLoading(true);
    setSelectedParetoOption("A");

    try {
      const res = await fetch(`${API_BASE_URL}/api/optimize`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: promptToUse,
          user_query: promptToUse,
          execution_mode: executionMode,
          dietary_preference: dietToUse,
          address_id: addrId,
          target_protein: proteinToUse,
          max_calories: caloriesToUse,
          max_budget: budgetToUse,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        setApiData(data);
        setTraceSteps(data.execution_traces || data.trace || []);
        if (data.state) {
          setHybridState(data.state);
        }
      } else {
        console.error("Optimization endpoint returned non-200 status");
      }
    } catch (err) {
      console.error("Error connecting to optimization server:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    async function init() {
      try {
        const res = await fetch(`${API_BASE_URL}/api/addresses`);
        if (res.ok) {
          const data = await res.json();
          if (data.addresses && data.addresses.length > 0) {
            setAddresses(data.addresses);
          }
        }
      } catch (err) {
        console.warn("Using sandbox addresses fallback:", err);
      }
      handleOptimize();
    }
    init();

    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === "SWIGGY_AUTH_SUCCESS" || event.data === "swiggy_oauth_success") {
        setIsMcpTokenActive(true);
        setExecutionMode("live_mcp");
        setShowOAuthModal(false);
        checkMcpToken();
      }
    };
    window.addEventListener("message", handleMessage);
    return () => window.removeEventListener("message", handleMessage);
  }, []);

  const handleDietaryPreferenceChange = (diet: DietaryType) => {
    setDietaryPreference(diet);
    handleOptimize(undefined, undefined, diet);
  };

  const handleAddressChange = (addressId: string) => {
    setSelectedAddressId(addressId);
    handleOptimize(undefined, addressId);
  };

  const handleReset = () => {
    setUserQuery("");
    setDietaryPreference("ALL");
    setHybridState(null);
    setApiData(null);
    setTraceSteps([]);
    setSelectedParetoOption("A");
    handleOptimize("", undefined, "ALL");
  };

  // Dynamic evaluation based on active Pareto selection (Option A vs Option B)
  const isPareto = apiData?.is_tradeoff_required ?? hybridState?.is_pareto_fallback ?? false;

  const activePlan = isPareto
    ? (selectedParetoOption === "A"
        ? (apiData?.option_a || hybridState?.pareto_options?.option_a)
        : (apiData?.option_b || hybridState?.pareto_options?.option_b))
    : (apiData?.active_recommendation || apiData?.option_a || hybridState);

  const displayFood = activePlan?.restaurant_dish || activePlan?.dish || activePlan?.food || hybridState?.selected_food_item;
  const displayInstamart = activePlan?.boosters || activePlan?.instamart || hybridState?.selected_instamart_items || [];
  const displayProtein = activePlan?.total_protein ?? activePlan?.total_p ?? activePlan?.protein ?? hybridState?.total_protein ?? 0;
  const displayCalories = activePlan?.total_calories ?? activePlan?.total_c ?? activePlan?.calories ?? hybridState?.total_calories ?? 0;
  const displayCarbs = activePlan?.total_carbs ?? hybridState?.total_carbs ?? 0;
  const displayFats = activePlan?.total_fats ?? hybridState?.total_fats ?? 0;
  const displaySubtotal = activePlan?.subtotal ?? hybridState?.items_subtotal ?? 0;
  const displayPayable = activePlan?.total_payable ?? activePlan?.cost ?? hybridState?.total_payable ?? 0;

  return (
    <div className="min-h-screen bg-[#090D14] text-zinc-100 flex flex-col pb-12" suppressHydrationWarning>
      {/* Main Consumer Header */}
      <Navbar
        addresses={addresses}
        selectedAddressId={selectedAddressId}
        setSelectedAddressId={handleAddressChange}
        onToggleDevDrawer={() => setIsDevDrawerOpen(!isDevDrawerOpen)}
        isDevDrawerOpen={isDevDrawerOpen}
      />

      {/* Main Content Workspace */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 w-full flex-1 flex flex-col lg:flex-row gap-6">
        {/* Left Sticky Sidebar Filters */}
        <SidebarFilters
          dietaryPreference={dietaryPreference}
          setDietaryPreference={handleDietaryPreferenceChange}
          targetProtein={targetProtein}
          setTargetProtein={(p) => {
            setTargetProtein(p);
            handleOptimize(undefined, undefined, undefined, p);
          }}
          maxCalories={maxCalories}
          setMaxCalories={(c) => {
            setMaxCalories(c);
            handleOptimize(undefined, undefined, undefined, undefined, c);
          }}
          maxBudget={maxBudget}
          setMaxBudget={(b) => {
            setMaxBudget(b);
            handleOptimize(undefined, undefined, undefined, undefined, undefined, b);
          }}
          onResetHistory={handleReset}
        />

        {/* Right Content Column */}
        <div className="flex-1 space-y-6">
          {/* Hero Banner */}
          <div className="bg-zinc-900/60 border border-zinc-800/80 rounded-2xl p-6 shadow-lg space-y-2">
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
              MacroFlow Cross-Fleet Engine
            </h1>
            <p className="text-xs sm:text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Autonomous agent optimizing high-protein meal combinations across restaurant food delivery and quick-commerce grocery fleets.
            </p>
          </div>

          {/* OAuth Banner / Modal (If Live MCP requested without active token) */}
          {executionMode === "live_mcp" && !isMcpTokenActive && (
            <div className="bg-zinc-900/90 border border-zinc-800 rounded-2xl p-6 shadow-xl text-center space-y-3">
              <div className="w-10 h-10 rounded-full bg-orange-500/10 text-[#FC8019] flex items-center justify-center mx-auto">
                <Zap className="w-5 h-5" />
              </div>
              <h3 className="text-base font-extrabold text-white">Connect Swiggy Account</h3>
              <p className="text-xs text-zinc-300 max-w-md mx-auto leading-relaxed">
                Connect your Swiggy account to stream live MCP staging tools (<code className="text-[#FC8019] bg-zinc-950 px-1.5 py-0.5 rounded">mcp.swiggy.com/food</code> + <code className="text-orange-400 bg-zinc-950 px-1.5 py-0.5 rounded">mcp.swiggy.com/im</code>).
              </p>
              <div className="pt-2 flex justify-center gap-3">
                <button
                  onClick={handleStartOAuth}
                  className="px-5 py-2.5 rounded-xl bg-[#FC8019] hover:bg-orange-600 text-white font-extrabold text-xs shadow-lg shadow-orange-500/20 flex items-center gap-2 cursor-pointer transition-all"
                >
                  <Link2 className="w-4 h-4" /> Authenticate via Swiggy OAuth
                </button>
                <button
                  onClick={() => handleSelectMode("sandbox")}
                  className="px-4 py-2.5 rounded-xl bg-zinc-800 hover:bg-zinc-700 text-zinc-300 text-xs font-semibold cursor-pointer transition-all"
                >
                  Use Sandbox Mode
                </button>
              </div>
            </div>
          )}

          {/* Clean Input Search Bar (Single Primary "Find Combos" CTA) */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleOptimize();
            }}
            className="flex gap-2"
            suppressHydrationWarning
          >
            <input
              id="user-macro-query"
              name="user_macro_query"
              type="text"
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
              placeholder={`Enter macro request (e.g. "${targetProtein}g protein under ₹${maxBudget} and <${maxCalories} kcal")`}
              autoComplete="off"
              data-m-id="user_macro_query"
              suppressHydrationWarning
              className="flex-1 bg-zinc-900/90 border border-zinc-800 rounded-xl px-4 py-3 text-xs sm:text-sm text-zinc-100 placeholder-zinc-500 focus:outline-none focus:border-[#FC8019] transition-colors"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="py-3 px-6 rounded-xl bg-[#FC8019] hover:bg-orange-600 disabled:opacity-50 text-white font-extrabold text-xs sm:text-sm shadow-lg shadow-orange-500/20 flex items-center gap-2 cursor-pointer transition-all shrink-0"
            >
              {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
              <span>Find Combos</span>
            </button>
          </form>

          {/* Loading State Skeletons */}
          {isLoading && (
            <div className="space-y-4 animate-pulse">
              <div className="h-28 bg-zinc-900/80 border border-zinc-800 rounded-2xl" />
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="h-48 bg-zinc-900/80 border border-zinc-800 rounded-2xl" />
                <div className="h-48 bg-zinc-900/80 border border-zinc-800 rounded-2xl" />
              </div>
              <div className="h-32 bg-zinc-900/80 border border-zinc-800 rounded-2xl" />
            </div>
          )}

          {/* Direct Visual Strategy Cards Workspace */}
          {!isLoading && hybridState && (
            <div className="space-y-6">
              {/* Pareto Trade-Off Cards with Tangible Food Previews & Option Selection */}
              {isPareto && (
                <ParetoCard
                  options={
                    apiData?.option_a
                      ? { option_a: apiData.option_a, option_b: apiData.option_b }
                      : (hybridState?.pareto_options || {})
                  }
                  targetProtein={targetProtein}
                  maxBudget={maxBudget}
                  selectedOption={selectedParetoOption}
                  onSelectOption={(opt) => setSelectedParetoOption(opt)}
                  goalGapText={apiData?.goal_gap_text || hybridState?.goal_gap_text}
                />
              )}

              {/* Split Cart Strategy View (Dynamically bound to active selection) */}
              <SplitCartDisplay
                recommendation={activePlan}
                foodItem={displayFood}
                instamartItems={displayInstamart}
                savings={activePlan?.savings || hybridState?.cost_savings_vs_single_fleet || 225}
                foodEta={hybridState?.food_eta_mins || 32}
                instamartEta={hybridState?.instamart_eta_mins || 12}
                isLoading={isLoading}
                isAlternative={apiData?.is_alternative || hybridState?.is_alternative}
              />

              {/* Macro Progress Breakdown Gauges */}
              <MacroGauges
                recommendation={activePlan}
                protein={displayProtein}
                targetProtein={targetProtein}
                calories={displayCalories}
                maxCalories={maxCalories}
                carbs={displayCarbs}
                fats={displayFats}
              />

              {/* Financial & Fee Accounting Table */}
              <FinancialTable
                recommendation={activePlan}
                itemsSubtotal={displaySubtotal}
                foodDeliveryFee={activePlan?.food_fee || hybridState?.food_delivery_fee || 35}
                instamartDeliveryFee={activePlan?.instamart_fee || hybridState?.instamart_delivery_fee || 15}
                taxesFees={activePlan?.taxes_platform || hybridState?.taxes_fees || 25}
                totalPayable={displayPayable}
                maxBudget={maxBudget}
              />

              {/* Dual Checkout Action Buttons */}
              <DualCheckoutButtons
                foodCartId={hybridState?.food_cart_id || "530602039"}
                instamartCartId={hybridState?.instamart_cart_id || "im_948201735"}
              />
            </div>
          )}
        </div>
      </main>

      {/* Discreet Slide-Over Sheet for Developer MCP Logs & Environment Controls */}
      <McpTerminalDrawer
        isOpen={isDevDrawerOpen}
        onClose={() => setIsDevDrawerOpen(false)}
        executionMode={executionMode}
        isMcpTokenActive={isMcpTokenActive}
        onSelectMode={handleSelectMode}
        traceSteps={traceSteps}
      />
    </div>
  );
}
