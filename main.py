#!/usr/bin/env python3
import os
import asyncio
import json
import re
from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, ConnectEvent, DisconnectEvent
import websockets

USERNAME = "elmananerobo"
PORT = 8080

client = TikTokLiveClient(unique_id=USERNAME)
connected_clients = set()

@client.on(ConnectEvent)
async def on_connect(event: ConnectEvent):
    print(f"📡 [TIKTOK] Conectado al Live de: {USERNAME}")

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

        if hasattr(event, 'user_info'):
            user_info = event.user_info
            unique_id = getattr(user_info, 'nick_name', '') or getattr(user_info, 'username', 'usuario')
            user_id = str(getattr(user_info, 'id', '0'))

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

        # Filtro radical existente
        unique_id = unique_id.replace('@', '')
        unique_id = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ ]', '', unique_id).strip()
        if not unique_id:
            unique_id = "usuario"

        # ✂️ Cortar a 8 caracteres estrictos en el backend
        nombre_noti = unique_id[:8].strip()

        # Log en PC para verificar el recorte exacto
        print(f"💬 {unique_id} [Noti: {nombre_noti}]: {comment_text}")

        # Enviamos ambos nombres por separado
        payload = json.dumps({
            "id_usuario": user_id,
            "nombre": unique_id,                 # Completo para el chat
            "nombre_notificacion": nombre_noti,  # 8 letras para la Mi Band
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
    print(f"📱 [WEBSOCKET] Nueva app conectada: {websocket.remote_address}")
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)
        print("❌ [WEBSOCKET] App desconectada.")

async def main():
    print(f"🔄 Iniciando servidores...")
    
    # Render asigna el puerto dinámicamente mediante variables de entorno
    # Si no encuentra la variable (en tu PC local), usará el 8080 por defecto
    port = int(os.environ.get("PORT", 8080))
    
    async with websockets.serve(android_handler, "::", port):
        print(f"🚀 Servidor WebSocket corriendo en el puerto: {port}")
        await client.connect()
        await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())