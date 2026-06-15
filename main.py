import asyncio
import os
import http
import websockets

async def health_check(path, request_headers):
    if "upgrade" not in request_headers.get("connection", "").lower():
        return http.HTTPStatus.OK, [], b"OK\n"

async def android_handler(websocket, path):
    async for message in websocket:
        pass

async def main():
    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Servidor en puerto {port}")  # <-- Este mensaje debe aparecer en logs
    async with websockets.serve(android_handler, "::", port, process_request=health_check):
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())