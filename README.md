# MacroFlow 🥗🤖

> **Autonomous AI Macro Assistant built for Swiggy Food & Instamart via Model Context Protocol (MCP)**

MacroFlow eliminates the friction of manually searching menus and calculating nutritional goals. Users provide natural fitness targets (e.g., *"Get me 40g of protein under 600 calories"*), and MacroFlow handles meal discovery, live cart management, and checkout sequentially using Swiggy's MCP server.

---

## 🌟 Demo & Submission
- **Live Demo Video (2 min):** [Google Drive Link](https://drive.google.com/file/d/1WcR_PVA_s1oQ0_E3oSYRhoEJkx7W0MRw/view?usp=sharing)
- **Built for:** Swiggy Builders Club

---

## 🏗️ Architecture Flow

```
[User Goal Prompt]
│
▼
[FastAPI Auth Middleware] ──(PKCE OAuth)──► [Swiggy Staging Auth]
│
▼
[LangGraph Agent Graph] ──(SSE Transport)──► [Swiggy MCP Server]
│                                            │
├──────► get_food_cart() ◄───────────────────┤
└──────► update_food_cart() ─────────────────┘ (Cart Mutated)
```

1. **OAuth 2.0 Authentication:** `auth_server.py` executes a secure PKCE handshake with Swiggy to acquire an SSE bearer token.
2. **Deterministic Agent Chaining:** `agent.py` uses LangGraph to filter MCP tools into a strict execution graph, preventing tool hallucination.
3. **Live State Mutation:** Connects to Swiggy's staging MCP server over SSE transport to mutate cart state, reserve inventory, compute delivery charges, and generate checkout links.

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Groq API Key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/divyanshgupta1141/macroflow-mvp.git
   cd macroflow-mvp
   ```

2. **Set up virtual environment & install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   ```bash
   cp .env.example .env
   # Add your GROQ_API_KEY inside .env
   ```

4. **Run the Auth Server:**
   ```bash
   uvicorn auth_server:app --reload --port 8000
   ```

5. **Run the Agent:**
   ```bash
   python agent.py
   ```

---

## 🛠️ Tech Stack

* **AI / Agent Framework:** LangGraph, LangChain, Groq (Llama-3.1-8B)
* **Protocol:** Swiggy Model Context Protocol (MCP over SSE)
* **Backend / Auth:** FastAPI, Uvicorn, httpx, PKCE OAuth 2.0
* **Language:** Python 3.14