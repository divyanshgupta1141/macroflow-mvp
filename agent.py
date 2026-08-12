import os
import json
import traceback
import httpx
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.prebuilt import create_react_agent
from mcp.client.streamable_http import streamable_http_client as http_client
from mcp import ClientSession
from mcp.shared.exceptions import McpError
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import tool
from tenacity import retry, wait_random_exponential, stop_after_attempt, retry_if_exception

load_dotenv()

# ==========================================
# Simulated Staging Tools (Safety Valve)
# ==========================================

@tool
def search_menu(query: str, location_id: str = "default") -> str:
    """Search for food items on Swiggy Staging Menu."""
    if "pizza" in query.lower():
        return json.dumps({
            "results": [
                {"item_id": "pizza_1", "name": "Protein Pepperoni Pizza", "restaurant": "Healthy Bakes", "macros": {"protein": "45g", "calories": 550}, "price": "$12.99"}
            ]
        })
    return json.dumps({
        "results": [
            {"item_id": "meal_1", "name": "Grilled Chicken Bowl", "restaurant": "FitBowl", "macros": {"protein": "50g", "calories": 500}, "price": "$10.99"}
        ]
    })

@tool
def add_to_cart(item_id: str, quantity: int = 1) -> str:
    """Add an item to the Swiggy cart."""
    return json.dumps({"status": "success", "cart_id": "cart_999", "message": f"Added {quantity} of {item_id} to cart."})

@tool
def get_checkout_url(cart_id: str = "cart_999") -> str:
    """Get the checkout URL for the current cart."""
    return json.dumps({"checkout_url": f"https://staging.swiggy.com/checkout/{cart_id}"})

@tool
def checkout_url(cart_id: str = "cart_999") -> str:
    """Get the checkout URL for the current cart."""
    return json.dumps({"checkout_url": f"https://staging.swiggy.com/checkout/{cart_id}"})

@tool
def get_food_cart(address_id: str | None = None, addressId: str | None = None) -> str:
    """Retrieve the current state of the food cart from the server."""
    return json.dumps({"cart_id": "cart_999", "items": []})

@tool
def update_food_cart(item_id: str | None = None, quantity: int | str = 1, address_id: str | None = None, addressId: str | None = None, restaurant_id: str | None = None, restaurantId: str | None = None, cartItems: list | dict | str | None = None) -> str:
    """Update item quantity in the Swiggy cart."""
    return json.dumps({"status": "success", "cart_id": "cart_999", "message": f"Updated cart."})

SIMULATED_TOOLS = [search_menu, add_to_cart, get_checkout_url, checkout_url, get_food_cart, update_food_cart]

# ==========================================
# Agent Execution Flow & Defensive Tool Logic
# ==========================================

# Note on Ephemeral Tool State (Swiggy Gateway Compliance):
# MCP tool outputs (restaurant menus, pricing, item availability, cart states)
# are fetched live per agent step and session. No tool output or response body
# is cached across user requests or loop iterations.

MOCK_TOKEN = None

def get_auth_base_url() -> str:
    """Dynamically derive the base auth server URL from REDIRECT_URI or AUTH_SERVER_URL env var, defaulting to render host."""
    redirect_uri = os.getenv("REDIRECT_URI", "")
    if redirect_uri and "/callback" in redirect_uri:
        return redirect_uri.rsplit("/callback", 1)[0]
    return os.getenv("AUTH_SERVER_URL", "https://macroflow-auth.onrender.com")

def get_swiggy_access_token():
    """Reads the token from the in-memory auth server store."""
    if MOCK_TOKEN is not None:
        return MOCK_TOKEN
    try:
        # Query the token server dynamically using the configured auth base URL
        base_url = get_auth_base_url()
        with httpx.Client() as client:
            response = client.get(f"{base_url}/token")
            if response.status_code == 200:
                return response.json().get("access_token")
    except Exception:
        pass
    return None

async def execute_agent_with_trace(swiggy_tools, user_input: str) -> tuple[str, list[dict]]:
    print(f"DEBUG: Agent received {len(swiggy_tools)} tools from Swiggy.")
    
    system_prompt = """You are a strict, single-pass execution agent for Swiggy Food & Instamart.
Step 1: Call `get_food_cart` passing `addressId`.
Step 2: Call `update_food_cart` passing `addressId`, `restaurantId`, and `cartItems`.
Step 3: Immediately STOP calling any tools. Parse the live numeric `cart_id` directly from the JSON response object returned by `update_food_cart`.
Step 4: Format your response cleanly in Markdown without raw timestamp strings. State:
Cart created successfully with ID **{cart_id}**!

https://www.swiggy.com/menu/924525"""
    
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=500
    )
    
    essential_tool_names = ["get_food_cart", "update_food_cart"]
    filtered_tools = [tool for tool in swiggy_tools if tool.name in essential_tool_names]
    agent = create_react_agent(llm, filtered_tools, prompt=system_prompt, debug=False)

    print("\n" + "=" * 55)
    print("🚀 MACROFLOW AGENT EXECUTION")
    print("=" * 55)
    response = await agent.ainvoke({"messages": [("user", user_input)]})
    trace_steps = []

    for msg in response["messages"]:
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"\n⚙️  [Agent Action]: Executing '{tc['name']}'...")
                print(f"    Args: {tc['args']}")
                trace_steps.append({
                    "type": "action",
                    "name": tc.get("name"),
                    "args": tc.get("args")
                })
        elif msg.type == "tool":
            print(f"\n✅ [Tool Result - {msg.name}]:")
            step = {"type": "result", "name": getattr(msg, "name", "tool")}
            if hasattr(msg, "artifact") and isinstance(msg.artifact, dict):
                struct = msg.artifact.get("structured_content") or msg.artifact
                data = struct.get("data") or {}
                status = struct.get("statusMessage") or struct.get("status", "SUCCESS")
                step["status"] = status
                print(f"    Status: {status}")
                if data.get("cart_id"):
                    step["cart_id"] = data.get("cart_id")
                    print(f"    Live Cart ID: {data.get('cart_id')}")
                if data.get("items"):
                    step["items"] = data.get("items")
                    print(f"    Item: {data['items'][0].get('name')}")
                if data.get("pricing"):
                    step["pricing"] = data.get("pricing")
                    print(f"    Total Payable: ₹{data['pricing'].get('to_pay')}")
            else:
                step["content"] = str(msg.content)[:200]
            trace_steps.append(step)

    final_msg = response["messages"][-1].content
    print("\n" + "-" * 55)
    print(f"🤖 [Final Output]:\n{final_msg}")
    print("-" * 55 + "\n")

    return final_msg, trace_steps

async def execute_agent(swiggy_tools, user_input: str) -> str:
    final_msg, _ = await execute_agent_with_trace(swiggy_tools, user_input)
    return final_msg


def should_retry(exception):
    print(f"DEBUG [Resiliency]: Checking exception for retry: {exception}")
    if isinstance(exception, BaseExceptionGroup):
        return any(should_retry(e) for e in exception.exceptions)
        
    if isinstance(exception, httpx.HTTPStatusError):
        status_code = exception.response.status_code
        return status_code == 429 or (500 <= status_code < 600)
    if isinstance(exception, (httpx.RequestError, McpError)):
        return True
    return False

@retry(
    wait=wait_random_exponential(multiplier=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception(should_retry),
    reraise=True
)
async def run_with_mcp_connection(headers, user_input):
    async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(45.0, read=120.0)) as async_client:
        async with http_client("https://mcp.swiggy.com/food", http_client=async_client) as (read_stream, write_stream, session_id):
            actual_session_id = session_id() if callable(session_id) else session_id
            print(f"DEBUG [Observability]: Swiggy Session ID captured: {actual_session_id}")
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                print("SUCCESS: Session Initialized")
                
                swiggy_tools = await load_mcp_tools(session)
                if not swiggy_tools:
                    print("STDOUT DEBUG: Tools empty, falling back to simulated.")
                    swiggy_tools = SIMULATED_TOOLS
                    
                return await execute_agent_with_trace(swiggy_tools, user_input)

async def process_request_detailed(user_input: str) -> tuple[str, list[dict]]:
    """Process a user request and return both final agent output and structured thought traces."""
    token = get_swiggy_access_token()
    base_auth_url = get_auth_base_url()
    
    if not token:
        return f"Authentication required. Please link your Swiggy account to continue: {base_auth_url}/login", []
        
    print(f"DEBUG: Attempting Official SSE POST Transport with token: {token[:10]}...")
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json, text/event-stream",
            "X-MCP-Protocol-Version": "2024-11-05"
        }
        return await run_with_mcp_connection(headers, user_input)
                
    except Exception as e:
        print("STDOUT DEBUG: Caught Exception in MCP execution flow after retries")
        traceback.print_exc()
        
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            try:
                with httpx.Client() as client:
                    client.post(f"{base_auth_url}/token/revoke")
            except Exception:
                pass
            return f"Session expired or unauthorized (401). Please re-authenticate via: {base_auth_url}/login", []
            
        print("STDOUT DEBUG: Falling back to simulated Swiggy tools for demo due to failure.")
        return await execute_agent_with_trace(SIMULATED_TOOLS, user_input)

async def process_request(user_input: str) -> str:
    """Process a user request using the agent, wrapped in an MCP connection."""
    final_msg, _ = await process_request_detailed(user_input)
    return final_msg

if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing agent...")
        
        # Fetch the real token from your running auth_server in memory
        try:
            base_url = get_auth_base_url()
            with httpx.Client() as client:
                token_response = client.get(f"{base_url}/token").json()
                token = token_response.get("access_token")
        except Exception:
            token = None
            
        global MOCK_TOKEN
        # If we got a real token from the running auth server, use it.
        # Otherwise, fall back to "mock_token_123" for local simulation.
        MOCK_TOKEN = token if token else "mock_token_123"
            
        user_input = (
            "My addressId is 'ctvea5srb5vobit8qosg'. Execute these exact steps:\n"
            "1. Call get_food_cart(addressId='ctvea5srb5vobit8qosg').\n"
            "2. Call update_food_cart(addressId='ctvea5srb5vobit8qosg', restaurantId='924525', cartItems=[{'menu_item_id': '201372805', 'quantity': 1}]).\n"
            "3. Do not call any further tools. Extract the live cart_id from Step 2's response and print 'https://www.swiggy.com/checkout/{cart_id}'."
        )
        res = await process_request(user_input)
        print(res)
        
        MOCK_TOKEN = None
            
    asyncio.run(test())
