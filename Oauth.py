import os

from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse

load_dotenv()

app = FastAPI()

session_secret = os.getenv("SESSION_SECRET")
client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")

if not session_secret or not client_id or not client_secret:
    raise RuntimeError("OAuth environment variables are missing")

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    same_site="lax",
    https_only=False,  # Local HTTP development only
)

oauth = OAuth()

oauth.register(
    name="google",
    client_id=client_id,
    client_secret=client_secret,
    server_metadata_url=(
        "https://accounts.google.com/.well-known/"
        "openid-configuration"
    ),
    client_kwargs={
        "scope": "openid email profile",
    },
)


@app.get("/")
def home():
    return {
        "message": "OAuth demo",
        "login_url": "/login",
    }


@app.get("/login")
async def login(request: Request):
    redirect_uri = (
        "http://127.0.0.1:8000/auth/callback"
    )

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri,
    )


@app.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        token = await oauth.google.authorize_access_token(
            request
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="OAuth authorization failed",
        )

    user = token.get("userinfo")

    if not user:
        raise HTTPException(
            status_code=400,
            detail="User information was not returned",
        )

    # Demonstration only: do not treat this response
    # as a persistent application login session.
    return {
        "message": "Google authorization successful",
        "user": {
            "sub": user.get("sub"),
            "email": user.get("email"),
            "name": user.get("name"),
        },
    }
