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
def get_checkout_url(cart_id: str) -> str:
    """Get the checkout URL for the current cart."""
    return json.dumps({"checkout_url": f"https://staging.swiggy.com/checkout/{cart_id}"})

SIMULATED_TOOLS = [search_menu, add_to_cart, get_checkout_url]

# ==========================================
# Agent Execution Flow
# ==========================================

def get_swiggy_access_token():
    """Reads the token from the .swiggy_token file."""
    if os.path.exists(".swiggy_token"):
        with open(".swiggy_token", "r") as f:
            return f.read().strip()
    return None

async def execute_agent(swiggy_tools, user_input: str) -> str:
    print(f"DEBUG: Agent received {len(swiggy_tools)} tools from Swiggy.")
    
    system_prompt = """
    You are the MacroFlow AI Nutrition Agent integrated with Swiggy. 
    RULES:
    1. Be conversational. Answer the user's specific request step-by-step. Do not rush to checkout unless asked.
    2. IMPORTANT: Do NOT call the get_addresses tool. Assume the user's location_id is always 'ctvea5srb5vobit8qosg' for all menu searches.
    3. Swiggy Server is the Source of Truth. If the user asks to review or checkout their cart, you MUST call `get_food_cart` to sync the state before generating the checkout URL.
    4. Format food items and URLs in clean HTML.
    """
    
    llm = ChatGroq(
        model="llama3-8b-8192",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0,
        max_tokens=500
    )
    
    agent = create_react_agent(llm, swiggy_tools, prompt=system_prompt, debug=True)
    print("DEBUG: LLM is now analyzing menu for macros...")
    response = await agent.ainvoke({"messages": [("user", user_input)]})
    return response["messages"][-1].content


async def process_request(user_input: str) -> str:
    """Process a user request using the agent, wrapped in an MCP connection."""
    token = get_swiggy_access_token()
    
    if not token:
        return "Authentication required. Please link your Swiggy account to continue: http://localhost:8000/login"
        
    print(f"DEBUG: Attempting Official SSE POST Transport with token: {token[:10]}...")
    
    swiggy_tools = None
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json, text/event-stream",
            "X-MCP-Protocol-Version": "2024-11-05"
        }
        # Harden the Read Stream with a robust timeout policy so large JSON payloads don't drop the connection
        async with httpx.AsyncClient(headers=headers, timeout=httpx.Timeout(45.0, read=120.0)) as async_client:
            async with http_client("https://mcp.swiggy.com/food", http_client=async_client) as (read_stream, write_stream, session_id):
                print(f"DEBUG [Observability]: Swiggy Session ID captured: {session_id}")
                async with ClientSession(read_stream, write_stream) as session:
                    await session.initialize()
                    print("SUCCESS: Session Initialized")
                    
                    swiggy_tools = await load_mcp_tools(session)
                    
                    if not swiggy_tools:
                        print("STDOUT DEBUG: Tools empty, falling back to simulated.")
                        swiggy_tools = SIMULATED_TOOLS
                        
                    return await execute_agent(swiggy_tools, user_input)
                
    except McpError as e:
        print(f"STDOUT DEBUG: Caught McpError: {e}")
        print("STDOUT DEBUG: Falling back to simulated Swiggy tools for demo.")
        swiggy_tools = SIMULATED_TOOLS
        return await execute_agent(swiggy_tools, user_input)
    except Exception as e:
        print("STDOUT DEBUG: Caught Exception in MCP Initialization")
        traceback.print_exc()
        
        error_str = str(e).lower()
        if "401" in error_str or "unauthorized" in error_str:
            if os.path.exists(".swiggy_token"):
                os.remove(".swiggy_token")
            return "Session expired or unauthorized (401). Please re-authenticate via: http://localhost:8000/login"
            
        print("STDOUT DEBUG: Falling back to simulated Swiggy tools for demo due to error.")
        swiggy_tools = SIMULATED_TOOLS
        return await execute_agent(swiggy_tools, user_input)

if __name__ == "__main__":
    import asyncio
    
    async def test():
        print("Testing agent...")
        with open(".swiggy_token", "w") as f:
            f.write("mock_token_123")
            
        res = await process_request("I just finished a heavy lift, get me 40g protein under 500 calories.")
        print(res)
        
        if os.path.exists(".swiggy_token"):
            os.remove(".swiggy_token")
            
    asyncio.run(test())
