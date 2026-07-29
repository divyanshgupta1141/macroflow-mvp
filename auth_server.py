import os
import base64
import hashlib
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()

# Temporary local cache for PKCE verifier
# In a production app, use Redis or a secure session store
auth_state = {}
TOKEN_STORE = {}

SWIGGY_CLIENT_ID = os.getenv("SWIGGY_CLIENT_ID", "mock_client_id")
REDIRECT_URI = "http://localhost:8000/callback"

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
    
    auth_url = (
        f"https://mcp.swiggy.com/auth/authorize?"
        f"response_type=code&"
        f"client_id={SWIGGY_CLIENT_ID}&"
        f"redirect_uri={REDIRECT_URI}&"
        f"code_challenge={challenge}&"
        f"code_challenge_method=S256&"
        f"scope=mcp:tools"
    )
    return RedirectResponse(url=auth_url)

@app.get("/callback")
async def callback(code: str):
    verifier = auth_state.get('verifier')
    if not verifier:
        raise HTTPException(status_code=400, detail="Missing code_verifier. Please start from /login again.")
    
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "code_verifier": verifier,
        "client_id": SWIGGY_CLIENT_ID,
        "redirect_uri": REDIRECT_URI
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
    uvicorn.run(app, host="localhost", port=8000)
