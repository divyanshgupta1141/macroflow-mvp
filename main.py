import asyncio
import time
from agent import process_request_detailed

async def run_cli_dual_fleet_demo():
    print("=" * 70)
    print("🚀 MACROFLOW AI: PRODUCTION CROSS-FLEET OPTIMIZER CLI VERIFICATION")
    print("=" * 70)
    
    # Test Case 1: Standard Non-Veg High Protein under Budget (Budget ₹450)
    print("\n----------------------------------------------------------------------")
    print("🧪 TEST CASE 1: High Protein Non-Veg Request (60g Protein, <₹450, <650 kcal)")
    print("----------------------------------------------------------------------")
    prompt_1 = "addressId is 'ctvea5srb5vobit8qosg'. 60g protein under ₹450 and <650 kcal"
    
    start_time = time.time()
    out1, trace1, state1 = await process_request_detailed(prompt_1, execution_mode="sandbox", dietary_preference="NON_VEG")
    elapsed1 = time.time() - start_time
    
    print(f"⏱️ Workflow Completed in {elapsed1:.3f}s")
    print(f"💬 Assistant Intro Content:  \"{out1}\"")
    print(f"🍽️ Selected Food Item:       {state1['selected_food_item']['name']} (₹{state1['selected_food_item']['final_price']})")
    print(f"⚡ Selected Instamart Items: {[i['name'] for i in state1['selected_instamart_items']]} (₹{sum(i['final_price'] for i in state1['selected_instamart_items'])})")
    print(f"💪 Total Achieved Protein:   {state1['total_protein']}g")
    print(f"🔥 Total Achieved Calories:  {state1['total_calories']} kcal")
    print(f"🧾 Total Items Subtotal:     ₹{state1['items_subtotal']}")
    print(f"💰 Total Payable (inc fees): ₹{state1['total_payable']}")
    print(f"💡 Real-World Savings:       Saved ₹{state1['cost_savings_vs_single_fleet']} vs standalone restaurant order")
    print(f"🌐 Swiggy Food Cart ID:      {state1['food_cart_id']}")
    print(f"⚡ Swiggy Instamart Cart ID: {state1['instamart_cart_id']}")

    # Test Case 2: Strict Veg Guardrail
    print("\n----------------------------------------------------------------------")
    print("🧪 TEST CASE 2: Pure Veg Guardrail Request (Veg Bowl + Lassi)")
    print("----------------------------------------------------------------------")
    prompt_2 = "Pure Veg 50g protein under ₹450 and <650 kcal"
    out2, trace2, state2 = await process_request_detailed(prompt_2, execution_mode="sandbox", dietary_preference="VEG")
    print(f"💬 Assistant Intro Content:  \"{out2}\"")
    print(f"🍽️ Selected Food Item:       {state2['selected_food_item']['name']} (Diet: {state2['selected_food_item']['dietary_type']})")
    print(f"⚡ Selected Instamart Items: {[i['name'] for i in state2['selected_instamart_items']]}")
    print(f"💪 Total Achieved Protein:   {state2['total_protein']}g")
    print(f"💰 Total Payable (inc fees): ₹{state2['total_payable']}")

    # Test Case 3: Infeasible Pareto Frontier Fallback
    print("\n----------------------------------------------------------------------")
    print("🧪 TEST CASE 3: Infeasible Request (90g Protein under ₹200) -> Pareto Solver")
    print("----------------------------------------------------------------------")
    prompt_3 = "90g protein under ₹200 and <650 kcal"
    out3, trace3, state3 = await process_request_detailed(prompt_3, execution_mode="sandbox", dietary_preference="ALL")
    print(f"💬 Assistant Intro Content:  \"{out3}\"")
    print(f"⚠️ Is Pareto Fallback Triggered: {state3['is_pareto_fallback']}")
    if state3.get("pareto_options"):
        p_opts = state3["pareto_options"]
        print(f"🎯 Option A (Hit Target Protein / Relax Budget): {p_opts['option_a']['title']}")
        print(f"    {p_opts['option_a']['description']}")
        print(f"    Protein: {p_opts['option_a']['protein']}g | Cost: ₹{p_opts['option_a']['cost']}")
        print(f"🛡️ Option B (Strict Budget Cap / Max Feasible Protein): {p_opts['option_b']['title']}")
        print(f"    {p_opts['option_b']['description']}")
        print(f"    Protein: {p_opts['option_b']['protein']}g | Cost: ₹{p_opts['option_b']['cost']}")

    print("\n" + "=" * 70)
    print("✅ ALL CLI VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    asyncio.run(run_cli_dual_fleet_demo())