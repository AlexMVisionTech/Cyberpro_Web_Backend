import sys
import os
import asyncio
import json
from io import BytesIO

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import app

# Passenger's WSGI interface does not send ASGI lifespan events. Run FastAPI's
# startup hooks before exposing the application so the database schema exists.
async def _initialize_app():
    async with app.router.lifespan_context(app):
        return


asyncio.run(_initialize_app())


class ASGIToWSGI:
    """Minimal synchronous WSGI adapter for the FastAPI HTTP application."""

    def __init__(self, asgi_app):
        self.asgi_app = asgi_app

    def __call__(self, environ, start_response):
        body = environ.get("wsgi.input", BytesIO()).read()
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        headers = []
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                headers.append((key[5:].replace("_", "-").lower().encode(), str(value).encode()))
        if environ.get("CONTENT_TYPE"):
            headers.append((b"content-type", environ["CONTENT_TYPE"].encode()))
        if environ.get("CONTENT_LENGTH"):
            headers.append((b"content-length", environ["CONTENT_LENGTH"].encode()))

        scope = {
            "type": "http",
            "asgi": {"version": "3.0", "spec_version": "2.3"},
            "http_version": environ.get("SERVER_PROTOCOL", "HTTP/1.1").replace("HTTP/", ""),
            "method": environ.get("REQUEST_METHOD", "GET"),
            "scheme": environ.get("wsgi.url_scheme", "http"),
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string.encode(),
            "root_path": "",
            "headers": headers,
            "client": (environ.get("REMOTE_ADDR", ""), 0),
            "server": (environ.get("SERVER_NAME", "localhost"), int(environ.get("SERVER_PORT", 80))),
        }
        messages = []
        request_sent = False

        async def receive():
            nonlocal request_sent
            if request_sent:
                return {"type": "http.disconnect"}
            request_sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message):
            messages.append(message)

        asyncio.run(self.asgi_app(scope, receive, send))
        response_start = next(m for m in messages if m["type"] == "http.response.start")
        response_body = b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body")
        status = response_start["status"]
        reason = {200: "OK", 201: "Created", 204: "No Content", 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found", 422: "Unprocessable Entity", 500: "Internal Server Error", 503: "Service Unavailable"}.get(status, "Unknown")
        start_response(f"{status} {reason}", [(k.decode().title(), v.decode()) for k, v in response_start.get("headers", [])])
        return [response_body]


application = ASGIToWSGI(app)
