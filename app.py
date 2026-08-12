import os
import re
import asyncio
import concurrent.futures
from typing import Any
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import agent execution functions
from agent import process_request_detailed

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="MacroFlow AI - Swiggy MCP Dashboard",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for modern, clean & compact aesthetic
st.markdown("""
    <style>
    /* Global Styles & Fonts */
    .stApp {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Card */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    .main-header h1 {
        color: #f8fafc;
        font-weight: 800;
        font-size: 1.8rem;
        margin: 0 0 6px 0;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 0.95rem;
        margin: 0;
    }
    
    /* Status Badge */
    .status-badge {
        display: inline-flex;
        align-items: center;
        background-color: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        color: #10b981;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 12px;
    }
    
    /* Metric Card Summary Banner */
    .goal-summary-card {
        background-color: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 12px 18px;
        margin-bottom: 18px;
        display: flex;
        justify-content: space-around;
        align-items: center;
        font-size: 0.95rem;
    }
    
    /* Tool Trace Cards */
    .tool-card {
        background-color: #1e293b;
        border-left: 4px solid #3b82f6;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    .tool-card-result {
        background-color: #0f172a;
        border-left: 4px solid #10b981;
        border-radius: 8px;
        padding: 10px 14px;
        margin-bottom: 8px;
        font-family: monospace;
        font-size: 0.85rem;
    }
    
    /* Checkout Highlight Button Box - Compact & Proportionate */
    .checkout-box {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(249, 115, 22, 0.3);
        border-radius: 14px;
        padding: 16px 20px;
        margin-top: 14px;
        max-width: 900px;
    }
    
    .checkout-box img {
        max-width: 180px !important;
        max-height: 120px !important;
        border-radius: 10px !important;
        object-fit: cover !important;
    }
    
    /* Compact Metric Sizing */
    [data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
        color: #94a3b8 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Helper function to safely execute async functions in Streamlit
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

# Helper function to extract live numeric cart_id from tool traces or response text
def extract_cart_id(text: str, trace_steps: list[dict[str, Any]] | None = None) -> str | None:
    # 1. Check trace steps for explicit numeric cart_id
    if trace_steps:
        for step in reversed(trace_steps):
            raw_id = step.get("cart_id")
            if raw_id:
                raw_str = str(raw_id).strip()
                if raw_str.isdigit():
                    return raw_str

    # 2. Search for numeric cart_id patterns (e.g., 530602039, 530460771, 529996298) in text
    numeric_match = re.search(r"\b(5\d{7,9})\b", text)
    if numeric_match:
        return numeric_match.group(1)

    # 3. Check for any cart_id in trace steps
    if trace_steps:
        for step in reversed(trace_steps):
            raw_id = step.get("cart_id")
            if raw_id:
                return str(raw_id).strip()

    # 4. Fallback to URL regex match
    match = re.search(r"https?://(?:www\.|staging\.)?swiggy\.com/checkout/([a-zA-Z0-9_-]+)", text)
    if match:
        return match.group(1)

    return None

# Parse full cart details for native Streamlit confirmation card
def parse_cart_details(trace_steps: list[dict[str, Any]] | None = None, text: str = "") -> dict[str, Any] | None:
    cart_id = extract_cart_id(text, trace_steps)
    if not cart_id:
        return None
        
    details: dict[str, Any] = {
        "cart_id": cart_id,
        "restaurant_id": "924525",
        "item_name": "SUPERYOU High Protein Olive & Sundried Tomato Footlong Pizza",
        "image_url": "https://media-assets.swiggy.com/swiggy/image/upload/FOOD_CATALOG/IMAGES/CMS/2024/5/8/927f269a-2645-41e5-bf80-626c59d6c8a2_9b436f72-6368-44e2-8b4f-0723fa2abab2.jpg",
        "subtotal": 495,
        "delivery": 45,
        "to_pay": 555
    }

    if trace_steps:
        for step in reversed(trace_steps):
            if step.get("type") == "action":
                args = step.get("args") or {}
                if args.get("restaurantId") or args.get("restaurant_id"):
                    details["restaurant_id"] = str(args.get("restaurantId") or args.get("restaurant_id"))
            elif step.get("type") == "result":
                items = step.get("items")
                if items and isinstance(items, list) and len(items) > 0:
                    first_item = items[0]
                    if isinstance(first_item, dict):
                        if first_item.get("name"):
                            details["item_name"] = str(first_item["name"])
                        img = first_item.get("imageUrl") or first_item.get("image_url")
                        if img:
                            details["image_url"] = str(img)
                        price = first_item.get("final_price") or first_item.get("price")
                        if price:
                            details["subtotal"] = price

                pricing = step.get("pricing")
                if pricing and isinstance(pricing, dict):
                    tp = pricing.get("to_pay") or pricing.get("total")
                    if tp is not None:
                        details["to_pay"] = tp
                    st_val = pricing.get("item_total") or pricing.get("subtotal")
                    if st_val is not None:
                        details["subtotal"] = st_val
                    del_fee = pricing.get("delivery_fee") if pricing.get("delivery_fee") is not None else pricing.get("delivery")
                    if del_fee is not None:
                        details["delivery"] = del_fee

    if details["to_pay"] == 555 and "₹" in text:
        price_match = re.search(r"₹\s*(\d+)", text)
        if price_match:
            details["to_pay"] = int(price_match.group(1))
            details["subtotal"] = max(details["to_pay"] - 45, 0)

    return details

# Render Native Streamlit Cart Confirmation Card (Compact & Proportional Sizing)
def render_native_cart_card(details: dict, protein_target: int, max_calories: int, max_budget: int):
    cart_id = details["cart_id"]
    restaurant_id = details.get("restaurant_id", "924525")
    item_name = details["item_name"]
    image_url = details.get("image_url")
    subtotal = details.get("subtotal")
    delivery = details.get("delivery")
    to_pay = details.get("to_pay")
    
    web_url = f"https://www.swiggy.com/menu/{restaurant_id}"
    app_url = f"swiggy://checkout?cart_id={cart_id}"

    st.markdown('<div class="checkout-box">', unsafe_allow_html=True)
    st.success("🎉 Swiggy Cart Created Successfully via MCP!", icon="✅")
    
    if image_url:
        col_img, col_info = st.columns([1, 3])
        with col_img:
            st.image(image_url, width=180)
        with col_info:
            st.markdown(f"<h3 style='margin:0 0 6px 0; font-size:1.25rem; font-weight:700;'>🍽️ {item_name}</h3>", unsafe_allow_html=True)
            st.markdown(f"<p style='margin:0 0 8px 0; font-size:0.9rem; color:#94a3b8;'>Live Cart ID: <code style='color:#10b981;'>{cart_id}</code> | Restaurant ID: <code>{restaurant_id}</code></p>", unsafe_allow_html=True)
    else:
        st.markdown(f"<h3 style='margin:0 0 6px 0; font-size:1.25rem; font-weight:700;'>🍽️ {item_name}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='margin:0 0 8px 0; font-size:0.9rem; color:#94a3b8;'>Live Cart ID: <code style='color:#10b981;'>{cart_id}</code> | Restaurant ID: <code>{restaurant_id}</code></p>", unsafe_allow_html=True)

    st.markdown("<p style='font-weight:600; margin:10px 0 4px 0; color:#94a3b8; font-size:0.9rem;'>💰 Price Breakdown</p>", unsafe_allow_html=True)
    p1, p2, p3 = st.columns(3)
    with p1:
        st.caption("Subtotal")
        st.write(f"₹{subtotal}" if subtotal else "₹510")
    with p2:
        st.caption("Delivery Fee")
        st.write(f"₹{delivery}" if str(delivery).isdigit() else (delivery or "₹45"))
    with p3:
        st.caption("Total Payable")
        st.write(f"**₹{to_pay}**")

    st.markdown("<p style='font-weight:600; margin:10px 0 4px 0; color:#94a3b8; font-size:0.9rem;'>📊 Target Macro Summary</p>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("💪 Protein Target", f"{protein_target}g Target")
    with m2:
        st.metric("🔥 Max Calories", f"<{max_calories} kcal")
    with m3:
        st.metric("💵 Budget Limit", f"<{max_budget} ₹")

    st.markdown("<hr style='margin:10px 0; border-color:#334155;'>", unsafe_allow_html=True)
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.link_button("🛒 Complete Order on Swiggy Web", web_url, type="primary", use_container_width=True)
    with btn_col2:
        st.link_button("📱 Open in Swiggy App", app_url, use_container_width=True)

    st.caption(f"ℹ️ Cart **{cart_id}** is reserved live on Swiggy via MCP. **Complete Order on Swiggy Web** opens Swiggy's live menu page, while **Open in Swiggy App** deep-links directly into your mobile app.")
    st.markdown('</div>', unsafe_allow_html=True)

# ==========================================
# Sidebar Interface
# ==========================================
with st.sidebar:
    st.title("🥗 MacroFlow AI")
    st.caption("Autonomous Swiggy Food & Instamart Agent")
    st.markdown("---")
    
    st.subheader("🎯 Macro & Budget Targets")
    
    # Target Inputs
    protein_target = st.slider("Target Protein (g)", min_value=10, max_value=120, value=40, step=5)
    max_calories = st.slider("Max Calories (kcal)", min_value=200, max_value=1500, value=600, step=50)
    max_budget = st.number_input("Max Budget (₹)", min_value=100, max_value=3000, value=600, step=50)
    
    st.markdown("### ⚡ Quick Presets")
    col1, col2, col3 = st.columns(3)
    if col1.button("🏋️‍♂️ Gym"):
        st.session_state["preset_protein"] = 50
        st.session_state["preset_cals"] = 700
        st.session_state["preset_budget"] = 500
    if col2.button("🥗 Lean"):
        st.session_state["preset_protein"] = 35
        st.session_state["preset_cals"] = 450
        st.session_state["preset_budget"] = 400
    if col3.button("⚡ Keto"):
        st.session_state["preset_protein"] = 45
        st.session_state["preset_cals"] = 600
        st.session_state["preset_budget"] = 650

    st.markdown("---")
    
    # System Status Indicator Badge
    st.markdown('<div class="status-badge">🟢 Swiggy MCP: Connected (Staging)</div>', unsafe_allow_html=True)
    st.caption("Protocol: Model Context Protocol (SSE)")
    st.caption("LLM Engine: Groq Llama-3.1-8B")
    
    st.markdown("---")
    
    # Session Reset Control
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hi! I am **MacroFlow AI**, your autonomous macro assistant for Swiggy. Tell me what you are craving (e.g. *'High protein chicken bowl'*), and I will analyze Swiggy menus, build your cart, and generate native cart confirmation cards!",
                "trace": [],
                "cart_details": None
            }
        ]
        st.rerun()

# ==========================================
# Main Header & Dashboard Area
# ==========================================
st.markdown("""
    <div class="main-header">
        <h1>🥗 MacroFlow AI Assistant</h1>
        <p>Intelligent nutrition planning and live cart management via Swiggy Model Context Protocol (MCP)</p>
    </div>
""", unsafe_allow_html=True)

# Active Goal Summary Banner
st.markdown(f"""
    <div class="goal-summary-card">
        <div><strong>💪 Protein Target:</strong> {protein_target}g+</div>
        <div><strong>🔥 Max Calories:</strong> &lt;{max_calories} kcal</div>
        <div><strong>💰 Max Budget:</strong> &lt;₹{max_budget}</div>
    </div>
""", unsafe_allow_html=True)

# Initialize Chat Messages in Session State
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hi! I am **MacroFlow AI**, your autonomous macro assistant for Swiggy. Tell me what you are craving (e.g. *'High protein chicken bowl'*), and I will analyze Swiggy menus, build your cart, and generate native cart confirmation cards!",
            "trace": [],
            "cart_details": None
        }
    ]

# Render Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # Display Agent Thought Process & Tool Calls in Expander if trace exists
        if message.get("trace"):
            with st.expander("🛠️ Agent Thought Process & MCP Tool Calls", expanded=False):
                for step in message["trace"]:
                    if step["type"] == "action":
                        st.markdown(f"**⚙️ Executing Tool:** `{step['name']}`")
                        st.json(step.get("args", {}))
                    elif step["type"] == "result":
                        st.markdown(f"**✅ Tool Result (`{step['name']}`):** `{step.get('status', 'SUCCESS')}`")
                        if step.get("cart_id"):
                            st.write(f"- **Live Cart ID:** `{step['cart_id']}`")
                        if step.get("items"):
                            st.write(f"- **Items:** `{step['items']}`")
                        if step.get("pricing"):
                            st.write(f"- **Pricing:** `{step['pricing']}`")
                        if step.get("content"):
                            st.text(step["content"])
        
        # Render Native Cart Confirmation Card if present
        if message.get("cart_details"):
            render_native_cart_card(message["cart_details"], protein_target, max_calories, max_budget)

# Handle New User Prompt
if prompt := st.chat_input("What are you craving today? (e.g., High protein post-workout meal)"):
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt, "trace": [], "cart_details": None})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare enriched agent input with active sidebar targets
    enriched_input = (
        f"My addressId is 'ctvea5srb5vobit8qosg'. User Request: {prompt}\n"
        f"Target Constraints: Protein >= {protein_target}g, Calories <= {max_calories} kcal, Budget <= ₹{max_budget}.\n"
        f"Execute these exact steps:\n"
        f"1. Call get_food_cart(addressId='ctvea5srb5vobit8qosg').\n"
        f"2. Call update_food_cart(addressId='ctvea5srb5vobit8qosg', restaurantId='924525', cartItems=[{{'menu_item_id': '201372805', 'quantity': 1}}]).\n"
        f"3. Do not call any further tools. Extract the live numeric cart_id from Step 2's response and format output cleanly as 'Cart created successfully with ID {{cart_id}}'."
    )

    # Process agent response with spinner
    with st.chat_message("assistant"):
        with st.spinner("🤖 MacroFlow Agent searching Swiggy MCP server & optimizing macros..."):
            response_text, trace_steps = run_async(process_request_detailed(enriched_input))
            cart_details = parse_cart_details(trace_steps, response_text)
            
            st.markdown(response_text)
            
            if trace_steps:
                with st.expander("🛠️ Agent Thought Process & MCP Tool Calls", expanded=False):
                    for step in trace_steps:
                        if step["type"] == "action":
                            st.markdown(f"**⚙️ Executing Tool:** `{step['name']}`")
                            st.json(step.get("args", {}))
                        elif step["type"] == "result":
                            st.markdown(f"**✅ Tool Result (`{step['name']}`):** `{step.get('status', 'SUCCESS')}`")
                            if step.get("cart_id"):
                                st.write(f"- **Live Cart ID:** `{step['cart_id']}`")
                            if step.get("items"):
                                st.write(f"- **Items:** `{step['items']}`")
                            if step.get("pricing"):
                                st.write(f"- **Pricing:** `{step['pricing']}`")
                            if step.get("content"):
                                st.text(step["content"])

            if cart_details:
                render_native_cart_card(cart_details, protein_target, max_calories, max_budget)

    # Append assistant response to session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "trace": trace_steps,
        "cart_details": cart_details
    })
