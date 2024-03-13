from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from config.db import _is_testing
from routes.users import router as user_router
from routes.commands import router as commands_router
from routes.devices import router as devices_router
import logging

logging.basicConfig(filename='logs.txt',
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

app = FastAPI()

app.include_router(user_router)
app.include_router(commands_router)
app.include_router(devices_router)

# test hello


@app.get("/")
async def root():
    return {"message": "Hello, TEST NEW!"}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware that logs incoming and outgoing requests.
    """
    logging.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Outgoing response: {response.status_code}")
    return response

origins = [
    "http://localhost:5173",
    "localhost:5173",
    "https://itx-app.com",
    "https://ppe.itx-app.com",
    "https://api.itx-app.com",
    "https://api.ppe.itx-app.com",
    "http://itx-app.com",
    "http://api.itx-app.com",
    "http://ppe.itx-app.com",
    "http://api.ppe.itx-app.com",
]

ALLOWED_HOSTS = [
    "https://itx-app.com",
    "https://ppe.itx-app.com",
    "https://api.itx-app.com",
    "https://api.ppe.itx-app.com",
    "http://itx-app.com",
    "http://api.itx-app.com",
    "http://ppe.itx-app.com",
    "http://api.ppe.itx-app.com",
    "http://localhost:5173",
    "localhost:5173",
    "*",
]

ALLOWED_HEADERS = ["*", "x-requested-with"]

app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=ALLOWED_HEADERS)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS if not _is_testing() else ["*"],)
