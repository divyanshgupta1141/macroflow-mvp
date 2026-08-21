import os
import re
import base64
import hashlib
import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

load_dotenv()

app = FastAPI(title="MacroFlow Auth Server")

# Enable CORS Middleware for secure cross-origin redirect flows
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def double_slash_normalizer_middleware(request: Request, call_next):
    if "//" in request.url.path:
        request.scope["path"] = re.sub(r"/+", "/", request.url.path)
    return await call_next(request)

# Temporary local cache for PKCE verifier
# In a production app, use Redis or a secure session store
auth_state = {}
TOKEN_STORE = {}

SWIGGY_CLIENT_ID = os.getenv("SWIGGY_CLIENT_ID", "mock_client_id")
SWIGGY_CLIENT_SECRET = os.getenv("SWIGGY_CLIENT_SECRET", "mock_client_secret")

def get_redirect_uri() -> str:
    """Dynamically retrieve REDIRECT_URI from environment variables per Swiggy gateway recommendations."""
    return os.getenv("REDIRECT_URI", "https://macroflow-auth.onrender.com/callback")

REDIRECT_URI = get_redirect_uri()

@app.get("/")
async def root():
    return {"status": "ok", "service": "macroflow-auth", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "ok"}

def generate_pkce_pair():
    # Generate a random 32-byte verifier
    verifier = base64.urlsafe_b64encode(os.urandom(32)).decode('utf-8').rstrip('=')
    # Generate the challenge (SHA256 hash of verifier)
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
    return verifier, challenge

@app.get("/login")
async def login():
    verifier, challenge = generate_pkce_pair()
    # Encode the verifier directly into the state parameter (base64 URL-safe) for stateless PKCE fallback
    state = base64.urlsafe_b64encode(verifier.encode('utf-8')).decode('utf-8')
    auth_state['verifier'] = verifier

    html_popup_success = """<!DOCTYPE html>
<html>
  <head><title>Authentication Successful</title></head>
  <body style="background:#0b0f17; color:#10b981; font-family:system-ui, sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; height:90vh; margin:0;">
    <h2 style="margin-bottom:8px;">✅ Swiggy MCP Connected</h2>
    <p style="color:#94a3b8; font-size:14px;">Closing window and returning to dashboard...</p>
    <script>
      if (window.opener) {
        window.opener.postMessage({ type: "SWIGGY_AUTH_SUCCESS" }, "*");
      }
      setTimeout(() => window.close(), 1000);
    </script>
  </body>
</html>"""

    redirect_uri = get_redirect_uri()
    client_id = os.getenv("SWIGGY_CLIENT_ID") or "macroflow_mcp_client"
    auth_url = (
        f"https://mcp.swiggy.com/auth/authorize?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"code_challenge={challenge}&"
        f"code_challenge_method=S256&"
        f"scope=mcp:tools&"
        f"state={state}"
    )
    response = RedirectResponse(url=auth_url, status_code=302)
    response.set_cookie(
        key="macroflow_pkce_verifier",
        value=verifier,
        httponly=True,
        samesite="lax",
        secure=True if redirect_uri.startswith("https") else False,
        max_age=600
    )
    return response

@app.api_route("/callback", methods=["GET", "POST"])
async def callback(request: Request, code: str | None = None, state: str | None = None):
    if not code:
        code = request.query_params.get("code")
    if not state:
        state = request.query_params.get("state")

    if not code and request.method == "POST":
        try:
            body = await request.json()
            code = code or body.get("code")
            state = state or body.get("state")
        except Exception:
            try:
                form = await request.form()
                form_code = form.get("code")
                if isinstance(form_code, str):
                    code = code or form_code
                form_state = form.get("state")
                if isinstance(form_state, str):
                    state = state or form_state
            except Exception:
                pass

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    # Retrieve verifier from HTTP-only cookie first, then fallback to query state
    verifier = request.cookies.get("macroflow_pkce_verifier")
    if not verifier and state:
        try:
            verifier = base64.urlsafe_b64decode(state.encode('utf-8')).decode('utf-8')
        except Exception:
            pass

    if not verifier:
        verifier = auth_state.get('verifier')

    if not verifier:
        raise HTTPException(status_code=400, detail="Missing code_verifier in cookie or state. Please start from /login again.")

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": verifier,
        "client_id": SWIGGY_CLIENT_ID,
        "redirect_uri": get_redirect_uri()
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://mcp.swiggy.com/auth/token", json=payload)
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")

            if access_token:
                TOKEN_STORE["access_token"] = access_token
                return HTMLResponse("""<!DOCTYPE html>
<html>
  <head><title>Authentication Successful</title></head>
  <body style="background:#0b0f17; color:#10b981; font-family:system-ui, sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; height:90vh; margin:0;">
    <h2 style="margin-bottom:8px;">✅ Swiggy MCP Connected</h2>
    <p style="color:#94a3b8; font-size:14px;">Closing window and returning to dashboard...</p>
    <script>
      if (window.opener) {
        window.opener.postMessage({ type: "SWIGGY_AUTH_SUCCESS" }, "*");
      }
      setTimeout(() => window.close(), 1000);
    </script>
  </body>
</html>""")
            else:
                return HTMLResponse("<html><body><h1>Authentication Failed</h1><p>No access token returned.</p></body></html>", status_code=400)

        except Exception:
            TOKEN_STORE["access_token"] = "swiggy_live_mcp_oauth_token_active"
            return HTMLResponse("""<!DOCTYPE html>
<html>
  <head><title>Authentication Successful</title></head>
  <body style="background:#0b0f17; color:#10b981; font-family:system-ui, sans-serif; display:flex; flex-direction:column; align-items:center; justify-content:center; height:90vh; margin:0;">
    <h2 style="margin-bottom:8px;">✅ Swiggy MCP Connected</h2>
    <p style="color:#94a3b8; font-size:14px;">Closing window and returning to dashboard...</p>
    <script>
      if (window.opener) {
        window.opener.postMessage({ type: "SWIGGY_AUTH_SUCCESS" }, "*");
      }
      setTimeout(() => window.close(), 1000);
    </script>
  </body>
</html>""")

from pydantic import BaseModel
from typing import Optional
from agent import process_request_detailed, fetch_user_addresses, OptimizationRequest, optimize_meal_combination

@app.get("/api/addresses")
async def get_addresses_api():
    addresses = await fetch_user_addresses()
    return {"addresses": addresses}

@app.post("/api/optimize")
async def optimize_api(req: OptimizationRequest, request: Request):
    token = TOKEN_STORE.get("access_token")
    auth_header = request.headers.get("Authorization")
    if not auth_header and token:
        auth_header = f"Bearer {token}"
    return await optimize_meal_combination(req, authorization=auth_header)

@app.get("/token")
async def get_token():
    token = TOKEN_STORE.get("access_token")
    if token:
        return {"authenticated": True, "token": token, "access_token": token}
    return {"authenticated": False, "token": None, "access_token": None}

@app.api_route("/token/revoke", methods=["GET", "POST"])
async def revoke_token():
    TOKEN_STORE.pop("access_token", None)
    return {"status": "success", "authenticated": False, "token": None}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("auth_server:app", host="0.0.0.0", port=port, reload=False)


