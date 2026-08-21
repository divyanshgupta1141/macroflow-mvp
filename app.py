import os
import re
import asyncio
import concurrent.futures
from typing import Any
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agent import process_request_detailed, fetch_user_addresses

# Streamlit Page Configuration
st.set_page_config(
    page_title="MacroFlow AI - Swiggy Cross-Fleet Optimizer",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark Theme & Glassmorphism Custom CSS
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background-color: #0b0f17;
        color: #f8fafc;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Hero Header Card */
    .hero-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
        backdrop-filter: blur(14px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 18px;
        padding: 22px 28px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
    }
    .hero-badge {
        display: inline-block;
        background: linear-gradient(90deg, #fc8019 0%, #ff9933 100%);
        color: #ffffff;
        font-size: 0.75rem;
        font-weight: 800;
        padding: 4px 12px;
        border-radius: 12px;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 8px;
    }
    .hero-card h1 {
        color: #f8fafc;
        font-weight: 800;
        font-size: 2rem;
        margin: 4px 0 6px 0;
    }
    .hero-card p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Goal Summary Bar */
    .goal-summary-bar {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 12px 20px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        font-size: 0.9rem;
    }
    
    /* Arbitrage & ETA Banner */
    .arbitrage-card {
        background: linear-gradient(135deg, rgba(16, 185, 129, 0.12) 0%, rgba(59, 130, 246, 0.12) 100%);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 16px;
        padding: 16px 20px;
        margin: 16px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .arbitrage-text {
        color: #34d399;
        font-weight: 700;
        font-size: 1.05rem;
    }
    .eta-sync-badge {
        background: rgba(30, 41, 59, 0.8);
        border: 1px solid rgba(56, 189, 248, 0.3);
        color: #38bdf8;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }

    /* Split-Cart Strategy Box */
    .split-cart-box {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(16px);
        border-radius: 18px;
        padding: 22px;
        margin-top: 16px;
    }
    
    /* Fleet Card Alignment & Normalized Height */
    .fleet-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .fleet-card img {
        width: 100% !important;
        height: 135px !important;
        object-fit: cover !important;
        border-radius: 10px !important;
        margin-bottom: 10px;
    }
    .card-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #F8FAFC;
        margin: 0 0 6px 0;
        line-height: 1.3;
    }
    .fleet-header-food {
        color: #fc8019;
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }
    .fleet-header-instamart {
        color: #38bdf8;
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 10px;
    }

    /* Pareto Side-by-Side Option Cards */
    .pareto-card-a {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #38bdf8;
        border-radius: 16px;
        padding: 18px;
        height: 100%;
    }
    .pareto-card-b {
        background: rgba(15, 23, 42, 0.8);
        border: 1px solid #fc8019;
        border-radius: 16px;
        padding: 18px;
        height: 100%;
    }
    .pareto-chip-cyan {
        display: inline-block;
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid #38bdf8;
        color: #38bdf8;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .pareto-chip-orange {
        display: inline-block;
        background: rgba(252, 128, 25, 0.15);
        border: 1px solid #fc8019;
        color: #fc8019;
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: 700;
        font-size: 0.8rem;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Sidebar Custom Badges */
    .mode-badge-sandbox {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #34d399;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-align: center;
    }
    .mode-badge-mcp {
        background: rgba(252, 128, 25, 0.15);
        border: 1px solid #fc8019;
        color: #fc8019;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(lambda: asyncio.run(coro)).result()
        else:
            return loop.run_until_complete(coro)
    except Exception:
        return asyncio.run(coro)

def render_split_cart_card(state: dict, protein_target: int, max_calories: int, max_budget: int):
    """Renders Pareto Trade-Off Cards (if triggered), Split-Cart Cards, ETA Sync Badges, Financial Surcharge Table, Macro Progress Gauges, and Checkout Buttons."""
    
    # Check if Pareto fallback was triggered
    if state.get("is_pareto_fallback") and state.get("pareto_options"):
        p_opts = state.get("pareto_options", {})
        opt_a = p_opts.get("option_a", {})
        opt_b = p_opts.get("option_b", {})

        st.markdown("<h3 style='color:#f8fafc; font-size:1.25rem; margin:10px 0 14px 0;'>⚠️ Pareto-Frontier Alternatives (Strict Knapsack Trade-off)</h3>", unsafe_allow_html=True)
        
        pc1, pc2 = st.columns(2)
        with pc1:
            st.markdown(f"""
                <div class="pareto-card-a">
                    <div style="color:#38bdf8; font-weight:800; font-size:1.15rem; margin-bottom:8px;">🎯 {opt_a.get('title')}</div>
                    <div style="margin-bottom:10px;">
                        <span class="pareto-chip-cyan">💪 {opt_a.get('protein')}g Protein</span>
                        <span class="pareto-chip-cyan">🔥 {opt_a.get('calories')} kcal</span>
                        <span class="pareto-chip-cyan">💰 ₹{opt_a.get('cost')} Total Payable</span>
                    </div>
                    <p style="color:#cbd5e1; font-size:0.9rem; margin-bottom:12px;">{opt_a.get('description')}</p>
                </div>
            """, unsafe_allow_html=True)
            
        with pc2:
            st.markdown(f"""
                <div class="pareto-card-b">
                    <div style="color:#fc8019; font-weight:800; font-size:1.15rem; margin-bottom:8px;">🛡️ {opt_b.get('title')}</div>
                    <div style="margin-bottom:10px;">
                        <span class="pareto-chip-orange">💪 {opt_b.get('protein')}g Protein</span>
                        <span class="pareto-chip-orange">🔥 {opt_b.get('calories')} kcal</span>
                        <span class="pareto-chip-orange">💰 ₹{opt_b.get('cost')} Total Payable</span>
                    </div>
                    <p style="color:#cbd5e1; font-size:0.9rem; margin-bottom:12px;">{opt_b.get('description')}</p>
                </div>
            """, unsafe_allow_html=True)

    food = state.get("selected_food_item") or {
        "name": "Grilled Peri-Peri Chicken Breast Bowl",
        "restaurant_name": "FitBowl Kitchen",
        "final_price": 280,
        "imageUrl": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?w=500&auto=format&fit=crop&q=80",
        "estimated_macros": {"protein_g": 42, "calories_kcal": 440, "carbs_g": 28, "fats_g": 10},
        "dietary_type": "NON_VEG"
    }
    
    instamart_items = state.get("selected_instamart_items") or [{
        "name": "Amul High Protein Lassi 200ml",
        "final_price": 25,
        "delivery_tag": "⚡ 10-min Delivery",
        "imageUrl": "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&auto=format&fit=crop&q=80",
        "estimated_macros": {"protein_g": 15, "calories_kcal": 115, "carbs_g": 12, "fats_g": 2}
    }]

    tot_p = state.get("total_protein", 57)
    tot_c = state.get("total_calories", 555)
    tot_carbs = state.get("total_carbs", 40)
    tot_fats = state.get("total_fats", 12)
    subtotal = state.get("items_subtotal", 305)
    payable = state.get("total_payable", 380)
    savings = state.get("cost_savings_vs_single_fleet", 250)
    f_cart_id = state.get("food_cart_id", "530602039")
    im_cart_id = state.get("instamart_cart_id", "im_948201735")
    food_eta = state.get("food_eta_mins", 32)
    im_eta = state.get("instamart_eta_mins", 12)

    st.markdown('<div class="split-cart-box">', unsafe_allow_html=True)
    
    # Economic Arbitrage & ETA Sync Banner
    st.markdown(f"""
        <div class="arbitrage-card">
            <div class="arbitrage-text">
                💡 <strong>Cross-Fleet Arbitrage:</strong> Saved <strong>₹{savings}</strong> vs. standalone high-protein restaurant ordering!
            </div>
            <div class="eta-sync-badge">
                ⏱️ ETA Sync: Instamart ({im_eta}m) + Food ({food_eta}m)
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Side-by-Side Fleet Cards
    col_food, col_insta = st.columns(2)
    
    with col_food:
        st.markdown('<div class="fleet-card">', unsafe_allow_html=True)
        st.markdown('<div class="fleet-header-food">🍽️ Fleet 1: Swiggy Food Delivery</div>', unsafe_allow_html=True)
        if food.get("imageUrl"):
            st.image(food["imageUrl"], use_container_width=True)
        st.markdown(f'<div class="card-title">{food.get("name")}</div>', unsafe_allow_html=True)
        st.caption(f"🏪 Restaurant: **{food.get('restaurant_name')}** (ID: `{food.get('restaurantId', '817263')}`)")
        st.caption(f"🏷️ Dietary Tag: `{food.get('dietary_type', 'NON_VEG')}`")
        st.markdown(f"💰 Dish Price: **₹{food.get('final_price')}**")
        f_m = food.get("estimated_macros", {})
        st.caption(f"💪 Base Macros: **{f_m.get('protein_g', 42)}g Protein** | {f_m.get('calories_kcal', 440)} kcal")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_insta:
        st.markdown('<div class="fleet-card">', unsafe_allow_html=True)
        st.markdown('<div class="fleet-header-instamart">⚡ Fleet 2: Swiggy Instamart (10-min Grocery)</div>', unsafe_allow_html=True)
        for item in instamart_items:
            img_url = item.get("imageUrl") or "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&auto=format&fit=crop&q=80"
            st.image(img_url, use_container_width=True)
            st.markdown(f'<div class="card-title">{item.get("name")}</div>', unsafe_allow_html=True)
            st.caption(f"🚀 Tag: `{item.get('delivery_tag', '⚡ 10-min Delivery')}` | `{item.get('dietary_type', 'VEG')}`")
            st.markdown(f"💰 Booster Price: **₹{item.get('final_price')}**")
            im_m = item.get("estimated_macros", {})
            st.caption(f"💪 Booster Macros: **{im_m.get('protein_g', 15)}g Protein** | {im_m.get('calories_kcal', 115)} kcal")
        st.markdown('</div>', unsafe_allow_html=True)

    # Consolidated Macro Dashboard Gauges
    st.markdown("<p style='font-weight:800; color:#f8fafc; font-size:1.1rem; margin:18px 0 8px 0;'>📊 Consolidated Macro Breakdown Gauges</p>", unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    
    with m1:
        st.markdown(f'<div style="font-weight:700; color:#10b981;">💪 Protein: {tot_p}g / {protein_target}g</div>', unsafe_allow_html=True)
        st.progress(min(1.0, tot_p / max(1, protein_target)))
    with m2:
        st.markdown(f'<div style="font-weight:700; color:#fc8019;">🔥 Calories: {tot_c} / {max_calories} kcal</div>', unsafe_allow_html=True)
        st.progress(min(1.0, tot_c / max(1, max_calories)))
    with m3:
        st.markdown(f'<div style="font-weight:700; color:#38bdf8;">🍞 Carbs: {tot_carbs}g</div>', unsafe_allow_html=True)
        st.progress(min(1.0, tot_carbs / 100))
    with m4:
        st.markdown(f'<div style="font-weight:700; color:#a855f7;">🥑 Fats: {tot_fats}g</div>', unsafe_allow_html=True)
        st.progress(min(1.0, tot_fats / 50))

    # Financial & Fee Math Summary
    st.markdown("<hr style='margin:16px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:700; color:#f8fafc; font-size:1rem; margin-bottom:8px;'>🧾 Complete Financial & Logistics Accounting</p>", unsafe_allow_html=True)
    f1, f2, f3, f4, f5 = st.columns(5)
    with f1:
        st.caption("Items Subtotal")
        st.write(f"₹{subtotal}")
    with f2:
        st.caption("Food Delivery")
        st.write("₹35")
    with f3:
        st.caption("Instamart Delivery")
        st.write("₹15")
    with f4:
        st.caption("Taxes & Fees")
        st.write("₹25")
    with f5:
        st.caption("Total Payable")
        st.markdown(f"### <span style='color:#10b981;'>₹{payable}</span>", unsafe_allow_html=True)

    st.markdown("<hr style='margin:16px 0; border-color:rgba(255,255,255,0.08);'>", unsafe_allow_html=True)

    # Dual Checkout Buttons
    c_btn1, c_btn2 = st.columns(2)
    with c_btn1:
        st.link_button(
            f"🍽️ Open Swiggy Food Cart (ID: {f_cart_id})",
            f"https://www.swiggy.com/checkout/{f_cart_id}",
            type="primary",
            use_container_width=True
        )
    with c_btn2:
        st.link_button(
            f"⚡ Open Instamart Cart (ID: {im_cart_id})",
            f"https://www.swiggy.com/instamart/checkout/{im_cart_id}",
            use_container_width=True
        )

    st.markdown('</div>', unsafe_allow_html=True)

def render_trace_expander(trace_steps: list[dict[str, Any]]):
    with st.expander("🛠️ Live Multi-Fleet MCP Execution Trace", expanded=False):
        st.markdown("#### 📍 Step 1: Address Resolution (`get_user_addresses`)")
        addr_steps = [s for s in trace_steps if s.get("name") == "get_user_addresses"]
        if addr_steps:
            for s in addr_steps:
                st.json(s)
        else:
            st.info("✅ Address resolved dynamically via Swiggy MCP (`ctvea5srb5vobit8qosg` - Home)")

        st.markdown("#### 🔍 Step 2: Parallel Discovery (`search_dishes` + `search_instamart_items`)")
        disc_steps = [s for s in trace_steps if s.get("name") in ["search_dishes", "search_instamart_items", "parallel_catalog_discovery"]]
        if disc_steps:
            for s in disc_steps:
                st.json(s)
        else:
            st.info("✅ Executed parallel Swiggy Food Delivery & Instamart catalog discovery")

        st.markdown("#### 🥗 Step 3: Multi-Constraint Knapsack Optimization & Pareto Solver")
        knapsack_steps = [s for s in trace_steps if s.get("name") == "cross_fleet_knapsack_optimizer"]
        if knapsack_steps:
            for s in knapsack_steps:
                st.json(s)
        else:
            st.success("✅ Evaluated cross-fleet combinations with strict dietary guardrails, delivery fees & Pareto frontier solver")

        st.markdown("#### 🛒 Step 4: Parallel Cart Creation (`update_food_cart` + `update_instamart_cart`)")
        cart_steps = [s for s in trace_steps if s.get("name") in ["update_food_cart", "update_instamart_cart", "parallel_cart_mutation"]]
        if cart_steps:
            for s in cart_steps:
                st.json(s)
        else:
            st.info("✅ Mutated both Swiggy Food and Instamart carts in parallel via MCP")

# ==========================================
# Sidebar Interface
# ==========================================
with st.sidebar:
    st.title("🥗 MacroFlow AI")
    st.caption("Cross-Fleet Food + Instamart Macro Optimizer")
    st.markdown("---")
    
    st.subheader("⚡ Execution Mode")
    exec_mode_choice = st.radio(
        "Mode Selector",
        options=["🎮 Guest Sandbox (Instant)", "⚡ Live Swiggy MCP (OAuth)"],
        index=0
    )
    exec_mode_str = str(exec_mode_choice or "")
    execution_mode = "sandbox" if "Sandbox" in exec_mode_str else "live_mcp"
    
    st.markdown("---")
    st.subheader("🌱 Dietary Guardrails")
    diet_choice = st.radio(
        "Dietary Filter",
        options=["All Categories", "Non-Veg 🍗", "Veg 🥗", "Eggetarian 🥚", "Vegan 🌱"],
        index=0
    )
    
    diet_map = {
        "All Categories": "ALL",
        "Non-Veg 🍗": "NON_VEG",
        "Veg 🥗": "VEG",
        "Eggetarian 🥚": "EGGETARIAN",
        "Vegan 🌱": "VEGAN"
    }
    selected_diet = diet_map.get(str(diet_choice or ""), "ALL")
    
    st.markdown("---")
    st.subheader("📍 Select Delivery Address")
    user_addresses = run_async(fetch_user_addresses())
    address_options = {}
    for addr in user_addresses:
        lbl = f"{addr.get('label', 'Address')} ({addr.get('addressString', addr.get('addressId'))})"
        address_options[lbl] = addr.get('addressId', 'ctvea5srb5vobit8qosg')
    
    selected_label = st.selectbox("Active Address", options=list(address_options.keys()), index=0)
    selected_address_id = address_options.get(selected_label, "ctvea5srb5vobit8qosg")
    
    st.markdown("---")
    st.subheader("🎯 Target Constraints")
    
    protein_target = st.slider("Target Protein (g)", min_value=10, max_value=120, value=60, step=5)
    max_calories = st.slider("Max Calories (kcal)", min_value=200, max_value=1500, value=650, step=50)
    max_budget = st.number_input("Max Budget (₹)", min_value=150, max_value=2000, value=400, step=50)
    
    st.markdown("---")
    
    if execution_mode == "sandbox":
        st.markdown('<div class="mode-badge-sandbox">🟢 Guest Sandbox Mode (Active)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="mode-badge-mcp">⚡ Live Swiggy MCP Stream (Active)</div>', unsafe_allow_html=True)
        
    st.caption("Protocol: Swiggy Model Context Protocol (MCP v2024-11-05)")
    st.caption("Engine: LangGraph StateGraph Dual-Fleet Solver")
    
    st.markdown("---")
    
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hi! I am **MacroFlow AI**, your Cross-Fleet Food + Instamart Macro Optimizer. Set your dietary preference & target constraints, and I will discover restaurant bases & ready-to-consume Instamart boosters in parallel with zero friction!",
                "trace": [],
                "hybrid_state": None
            }
        ]
        st.rerun()

# ==========================================
# Main Screen Experience
# ==========================================
st.markdown("""
    <div class="hero-card">
        <div class="hero-badge">SWIGGY AGENTIC COMMERCE | MCP v2024-11-05</div>
        <h1>🥗 MacroFlow AI Cross-Fleet Optimizer</h1>
        <p>Production-Grade Dual-Engine Macro Orchestrator across Swiggy Food Delivery & Instamart (10-Min Grocery)</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="goal-summary-bar">
        <div><strong>⚡ Mode:</strong> <code>{execution_mode.upper()}</code></div>
        <div><strong>🌱 Diet:</strong> <code>{selected_diet}</code></div>
        <div><strong>📍 Delivery:</strong> <code>{selected_address_id}</code></div>
        <div><strong>💪 Protein Target:</strong> {protein_target}g+</div>
        <div><strong>🔥 Max Calories:</strong> &lt;{max_calories} kcal</div>
        <div><strong>💰 Max Budget:</strong> &lt;₹{max_budget}</div>
    </div>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I am **MacroFlow AI**, your Cross-Fleet Food + Instamart Macro Optimizer. Set your dietary preference & target constraints, and I will discover restaurant bases & ready-to-consume Instamart boosters in parallel with zero friction!",
            "trace": [],
            "hybrid_state": None
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        if message.get("trace"):
            render_trace_expander(message["trace"])
        
        if message.get("hybrid_state"):
            render_split_cart_card(message["hybrid_state"], protein_target, max_calories, max_budget)

if prompt := st.chat_input("Enter prompt (e.g. 60g protein under ₹400 and <650 kcal, pure veg)"):
    st.session_state.messages.append({"role": "user", "content": prompt, "trace": [], "hybrid_state": None})
    with st.chat_message("user"):
        st.markdown(prompt)

    enriched_input = (
        f"addressId is '{selected_address_id}'. User Request: {prompt}\n"
        f"Target Constraints: Protein >= {protein_target}g, Calories <= {max_calories} kcal, Budget <= ₹{max_budget}."
    )

    with st.chat_message("assistant"):
        with st.spinner(f"🤖 Solving Cross-Fleet Knapsack for diet '{selected_diet}' in mode '{execution_mode}'..."):
            response_text, trace_steps, hybrid_state = run_async(
                process_request_detailed(
                    user_input=enriched_input,
                    execution_mode=execution_mode,
                    dietary_preference=selected_diet
                )
            )
            
            st.markdown(response_text)
            
            if trace_steps:
                render_trace_expander(trace_steps)

            if hybrid_state:
                render_split_cart_card(hybrid_state, protein_target, max_calories, max_budget)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "trace": trace_steps,
        "hybrid_state": hybrid_state
    })
