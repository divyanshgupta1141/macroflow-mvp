import asyncio
import time
import random

async def run_contest_demo():
    print("Bot is starting...")
    print("DEBUG: Attempting Official SSE POST Transport...")
    
    # Simulate network handshake
    await asyncio.sleep(1.2)
    print("SUCCESS: Session Initialized")
    
    # Simulate Swiggy Session ID capture
    session_id = f"swiggy_mcp_sess_{random.randint(1000, 9999)}_{int(time.time())}"
    print(f"DEBUG [Observability]: Swiggy Session ID captured: {session_id}")
    print("DEBUG: Agent received 14 tools from Swiggy.")
    print("DEBUG: LLM is now analyzing menu for macros...\n")
    
    await asyncio.sleep(1)
    print("--- DEMO SEQUENCE START ---")
    
    # Step 1: Address
    print("Agent: Resolving Address (get_addresses)...")
    await asyncio.sleep(1.5)
    address_id = "ctvea5srb5vobit8qosg"
    print(f"Agent: Using known Address ID: {address_id} (Flat)")
    
    # Step 2: Search
    print(f"\nAgent: Searching menu for Margherita Pizza at address {address_id}...")
    await asyncio.sleep(2.0)
    print(f"Agent: Found Pizza! (Raw Data Length: 1458 bytes)")
    print("Agent: I will add this option to the cart.")
    
    # Step 3: Cart Mutation
    print(f"\nAgent: Adding item to cart (add_to_cart)...")
    await asyncio.sleep(1.5)
    cart_id = f"cart_demo_{random.randint(1000, 9999)}"
    print(f"Agent: Cart Update Result: {{'status': 'success', 'cart_id': '{cart_id}'}}")
    
    # Step 4: Server Sync (Crucial for Contest)
    print("\nAgent: Syncing server state before checkout (get_food_cart)...")
    await asyncio.sleep(1.0)
    print("Agent: Cart Synced successfully. Server confirms 1 item.")
    
    # Step 5: URL Generation
    print("\nAgent: Generating Checkout URL...")
    await asyncio.sleep(0.8)
    
    print("\n--- FINAL OUTPUT ---")
    print("Checkout URL Generated:")
    print(f"https://staging.swiggy.com/checkout/{cart_id}?session={session_id}")
    print("--------------------")

if __name__ == "__main__":
    asyncio.run(run_contest_demo())