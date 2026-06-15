import asyncio
import os
import http
import websockets
from websockets.http11 import Request

async def health_check(connection, request):
    # Interceptar peticiones HEAD y GET que NO son upgrades WebSocket
    upgrade_header = request.headers.get("upgrade", "").lower()
    if upgrade_header != "websocket":
        # Responder 200 OK para que Render sepa que el servicio está vivo
        response_headers = [
            ("Content-Type", "text/plain"),
            ("Content-Length", "2"),
        ]
        return connection.respond(http.HTTPStatus.OK, b"OK")
    # Si es un WebSocket real, devolver None para continuar el handshake
    return None

async def android_handler(websocket):
    async for message in websocket:
        pass

async def main():
    print("🔄 Iniciando servidores...")
    
    port = int(os.environ.get("PORT", 8080))
    
    async with websockets.serve(
        android_handler,
        "::",
        port,
        process_request=health_check
    ):
        print(f"🚀 Servidor WebSocket corriendo en el puerto: {port}")
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario.")