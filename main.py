#!/usr/bin/env python3
import asyncio
import json
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent, DisconnectEvent
import websockets

# Configuración
USERNAME = "pericoclips2"
PORT = 8080

client = TikTokLiveClient(unique_id=USERNAME)
connected_clients = set()

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"📡 [TIKTOK] Conectado al Live de: @{USERNAME}")

@client.on(DisconnectEvent)
async def on_disconnect(event: DisconnectEvent):
    print("⚠️ [TIKTOK] Conexión perdida con TikTok.")

@client.on(CommentEvent)
async def on_comment(event: CommentEvent):
    try:
        unique_id = "usuario"
        user_id = "0"
        comment_text = getattr(event, 'comment', '') or getattr(event, 'comment_text', '')

        if not comment_text:
            return

        # Extracción directa basada en la estructura actual de TikTok
        if hasattr(event, 'user_info'):
            user_info = event.user_info
            
            # Buscar el nombre por 'nick_name' o 'username'
            unique_id = getattr(user_info, 'nick_name', '') or getattr(user_info, 'username', 'usuario')
            user_id = str(getattr(user_info, 'id', '0'))

        # Si aún así falla, extracción manual desde el texto crudo
        if unique_id == "usuario":
            try:
                raw_data = str(event)
                if "nick_name=" in raw_data:
                    unique_id = raw_data.split("nick_name=")[1].split(",")[0].replace("'", "").replace('"', '').strip()
                elif "username=" in raw_data:
                    unique_id = raw_data.split("username=")[1].split(",")[0].replace("'", "").replace('"', '').strip()
                
                if "id=" in raw_data:
                    user_id = raw_data.split("id=")[1].split(",")[0].strip()
            except Exception:
                pass

        print(f"💬 @{unique_id}: {comment_text}")

        payload = json.dumps({
            "id_usuario": user_id,
            "nombre": unique_id, 
            "avatar_url": "",
            "mensaje": comment_text
        })
        
        if connected_clients:
            await asyncio.gather(*[
                ws.send(payload) for ws in connected_clients 
                if hasattr(ws, 'state') and ws.state.name == "OPEN"
            ])
            
    except Exception as e:
        print(f"❌ Error al procesar comentario: {e}")

async def android_handler(websocket):
    print(f"📱 [WEBSOCKET] Nueva app Android conectada: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print("❌ [WEBSOCKET] App Android desconectada.")

async def main():
    print(f"🔄 Iniciando servidores...")
    async with websockets.serve(android_handler, "0.0.0.0", PORT):
        print(f"🚀 Servidor WebSocket corriendo en el puerto {PORT}")
        await client.connect()
        await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️ Servidor detenido.")