import os
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
    # Save the verifier associated with this flow
    auth_state['verifier'] = verifier
    
    redirect_uri = get_redirect_uri()
    auth_url = (
        f"https://mcp.swiggy.com/auth/authorize?"
        f"response_type=code&"
        f"client_id={SWIGGY_CLIENT_ID}&"
        f"redirect_uri={redirect_uri}&"
        f"code_challenge={challenge}&"
        f"code_challenge_method=S256&"
        f"scope=mcp:tools"
    )
    return RedirectResponse(url=auth_url)

@app.api_route("/callback", methods=["GET", "POST"])
async def callback(request: Request, code: str | None = None):
    # Extract code from query params or request body for POST requests
    if not code and request.method == "POST":
        try:
            body = await request.json()
            code = body.get("code")
        except Exception:
            try:
                form = await request.form()
                code = form.get("code")
            except Exception:
                pass

    if not code:
        raise HTTPException(status_code=400, detail="Missing authorization code.")

    verifier = auth_state.get('verifier')
    if not verifier:
        raise HTTPException(status_code=400, detail="Missing code_verifier. Please start from /login again.")
    
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
                return HTMLResponse("<html><body><h1>Authentication Successful!</h1><p>You can now return to the Telegram bot.</p></body></html>")
            else:
                return HTMLResponse("<html><body><h1>Authentication Failed</h1><p>No access token returned.</p></body></html>", status_code=400)
                
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Token request failed: {e.response.text}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get("/token")
async def get_token():
    return {"access_token": TOKEN_STORE.get("access_token")}

@app.post("/token/revoke")
async def revoke_token():
    TOKEN_STORE.pop("access_token", None)
    return {"status": "success"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("auth_server:app", host="0.0.0.0", port=port, reload=False)


