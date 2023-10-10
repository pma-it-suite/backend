from fastapi import FastAPI, Request
from routes.users import router as user_router
import logging

logging.basicConfig(filename='logs.txt',
                    level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

app = FastAPI()

app.include_router(user_router)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Middleware that logs incoming and outgoing requests.
    """
    logging.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logging.info(f"Outgoing response: {response.status_code}")
    return response


@app.get("/")
async def root():
    return {"message": "Hello World"}


"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Run the app in debug or production mode.')
    parser.add_argument('--debug',
                        type=bool,
                        default=False,
                        help='Run in debug mode.')
    args = parser.parse_args()

    SERVER_HOST = 'localhost' if args.debug else '0.0.0.0'
    SERVER_PORT = 8080 if args.debug else '5001'

    if args.debug:
        app.run(debug=True, host=SERVER_HOST, port=SERVER_PORT)
    else:
        file_base = "/var/lib/caddy/.local/share/caddy/certificates/acme-v02.api.letsencrypt.org-directory/its.kdns.ooo/its.kdns.ooo"
        cert = file_base + ".crt"
        key = file_base + ".key"
        context = (cert, key)
        app.run(debug=False,
                host=SERVER_HOST,
                port=SERVER_PORT,
                ssl_context=context)
"""
