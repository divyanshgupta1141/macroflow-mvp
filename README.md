# MacroFlow 🥗🤖

> **Autonomous Nutrition-Guided Ordering Agent built on Swiggy's Staging Model Context Protocol (MCP) using LangGraph State Machines.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangGraph](https://img.shields.io/badge/Orchestration-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Protocol](https://img.shields.io/badge/Protocol-Model_Context_Protocol_(MCP)-green.svg)](https://modelcontextprotocol.io/)
[![Hackathon](https://img.shields.io/badge/Selected_Builder-Swiggy_Builders_Club-red.svg)](#)

---

## 📺 60-Second Demo & Architecture Walkthrough

<!-- Replace the link below with your 45-60s Loom recording or embed an optimized GIF -->
> **[▶️ Watch 60-Second Technical Demo (Loom)](https://www.loom.com/YOUR_DEMO_LINK)**  
> *Demonstrates: Natural language dietary intent parsing → MCP tool execution → In-memory cache hit → Check-then-Mutate cart synchronization.*

* **Live Deployment:** [macroflow-mvp.vercel.app](https://macroflow-mvp.vercel.app/)
* **Context:** Built and selected for the **Swiggy Builders Club**.

---

## 🏗️ System Architecture

MacroFlow models the food discovery and checkout lifecycle as a deterministic, cyclic state graph. It interfaces with Swiggy's staging environment via Model Context Protocol (MCP) over Server-Sent Events (SSE) transport.

```mermaid
flowchart TD
    User([User Prompt: '40g protein under 600 kcal']) --> Auth[FastAPI PKCE Auth Handshake]
    Auth --> Agent[LangGraph State Machine: agent.py]
    
    subgraph Optimization & Caching Layer
        Agent --> CacheQuery{Check SKU_CACHE}
        CacheQuery -- Cache Hit (<400ms) --> Eval[Macro & Inventory Evaluation]
        CacheQuery -- Cache Miss --> MCP_Fetch[Fetch Catalog via Swiggy MCP]
        MCP_Fetch --> CacheUpdate[Store in In-Memory SKU Cache (1h TTL)]
        CacheUpdate --> Eval
    end

    subgraph Deterministic Checkout Guard
        Eval --> PreFlight[1. Check: Verify Server Cart State & Pricing]
        PreFlight --> SwiggyAPI[(Swiggy Backend Source of Truth)]
        SwiggyAPI -- State Validated --> Mutate[2. Mutate: Atomic Cart Update Dispatch]
        SwiggyAPI -- HTTP 429 Rate Limit --> Backoff[Exponential Backoff & Fallback Engine]
        Backoff --> StateRollback[LangGraph Checkpoint Rollback]
    end

    Mutate --> Result([Synchronized Cart & Checkout Link])
```

---

## 🛡️ Core Engineering & Reliability Patterns

### 1. "Check-then-Mutate" Deterministic Cart Synchronization
Multi-fleet commerce systems (Swiggy Food and Instamart) suffer from state drift when client-side carts fall out of sync with volatile restaurant inventories:
* **Pre-Flight Validation:** Before compiling any checkout payload, the LangGraph node executes pre-flight checks against active cart endpoints (`get_food_cart`, `get_instamart_cart`), treating the remote backend as the single source of truth.
* **Atomic Mutation Dispatch:** State updates are dispatched only after real-time SKU availability, minimum order limits, and delivery constraints are validated. If pricing or stock has drifted, the agent halts mutation and triggers a re-ranking loop.

### 2. In-Memory SKU & Macro Caching
Multi-turn conversational optimization (e.g., swapping sides, recalibrating protein targets) creates redundant remote network calls:
* **In-Memory TTL Cache:** Implemented an in-memory dictionary cache (`SKU_CACHE`) with a 1-hour time-to-live (`SKU_CACHE_TTL_SECONDS = 3600`) covering verified booster items, restaurant menu dishes, and macro nutritional heuristics.
* **Network Roundtrip Elimination:** Pre-flight cache hits bypass external HTTP hops entirely, resolving conversational adjustments locally while seamlessly routing cache misses to live MCP tools.

### 3. Multi-Tiered Fallback Engine & HTTP 429 Handling
Staging gateways and quick-commerce APIs experience aggressive rate-limiting under burst traffic:
* **Exponential Backoff & Interception:** All external MCP network calls are routed through an interceptor that detects HTTP 429 (Too Many Requests), respects `Retry-After` headers, and applies jittered exponential backoff retries.
* **Graceful Catalog Fallback:** If upstream network timeouts or rate limits exhaust retries, the agent falls back to a verified offline catalog (`INSTAMART_BOOSTER_CATALOG`) and macro heuristics, avoiding unhandled exceptions or dropped user sessions.

---

## 📂 Key Code & Architecture Pointers

Inspect the core architectural patterns directly:

| Component | File Link | Description |
| :--- | :--- | :--- |
| **Agent State Graph** | [`agent.py`](agent.py) | LangGraph workflow definition, node transitions, and MCP tool binding |
| **Cart Guards & Caching** | [`agent.py`](agent.py) | In-memory `SKU_CACHE` implementation and Check-then-Mutate logic |
| **OAuth & PKCE Gateway** | [`auth_server.py`](auth_server.py) | FastAPI auth middleware handling Swiggy PKCE handshake and SSE token exchange |
| **Dependencies & Config** | [`requirements.txt`](requirements.txt) | Pinned versions for LangGraph, FastAPI, and MCP client libraries |

---

## 🚀 Local Setup & Execution

### Prerequisites
* Python 3.11+
* Groq API Key (for Llama-3.1 inference)

### 1. Clone & Set Up Virtual Environment
```bash
git clone https://github.com/divyanshgupta1141/macroflow-mvp.git
cd macroflow-mvp

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory:
```bash
cp .env.example .env
```
Ensure your `.env` contains:
```env
GROQ_API_KEY=your_groq_api_key_here
SWIGGY_MCP_BASE_URL=[https://staging-mcp.swiggy.com]
PORT=8000
```

### 3. Launch Services

**Terminal 1 — Auth & Webhook Server:**
```bash
uvicorn auth_server:app --reload --port 8000
```

**Terminal 2 — Run the Agent:**
```bash
python agent.py
```

---

## 🧪 Sample CLI Interaction Trace

```text
[User] "Find me a post-workout dinner: 45g protein, under 700 kcal near Indiranagar"
[Agent] Querying in-memory cache... (Miss)
[MCP] Dispatched search_live_dishes (Swiggy Food SSE Transport)
[Agent] Evaluated 12 SKUs -> Selected Grilled Chicken Bowl (42g P, 520 kcal)
[Agent] Executing Pre-flight Check: get_food_cart() -> Server state: Cart Empty
[Agent] Check-then-Mutate Verified -> Dispatched update_food_cart()
[Success] Cart synchronized. Checkout URL generated: [https://swiggy.com/pay/](https://swiggy.com/pay/)...
```

---

## 🛠️ Tech Stack

* **Orchestration:** LangGraph (State Graphs, Cyclic Checkpoints), LangChain
* **LLM Engine:** Groq (Llama-3.1-8B-Instant)
* **Protocol & Transport:** Model Context Protocol (MCP) over SSE (Server-Sent Events)
* **Backend & Auth:** FastAPI, Uvicorn, httpx, OAuth 2.0 (PKCE)
* **Language & Validation:** Python 3.11+, Pydantic v2
