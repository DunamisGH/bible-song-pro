#!/usr/bin/env python3
import argparse
import asyncio
import json
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import websockets
from websockets.server import WebSocketServerProtocol

ROOT = Path(__file__).resolve().parent

clients = set()


async def broadcast(sender, message: str) -> None:
    other_clients = [ws for ws in list(clients) if ws is not sender]
    for ws in other_clients:
        try:
            await ws.send(message)
        except Exception:
            clients.discard(ws)


async def websocket_handler(websocket: WebSocketServerProtocol):
    clients.add(websocket)
    try:
        async for raw_message in websocket:
            if not raw_message:
                continue
            try:
                payload = json.loads(raw_message)
            except json.JSONDecodeError:
                continue
            if not isinstance(payload, dict):
                continue
            await broadcast(websocket, json.dumps(payload, separators=(",", ":")))
    finally:
        clients.discard(websocket)


def start_http_server(host: str, port: int):
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    httpd = ThreadingHTTPServer((host, port), handler)
    print(f"HTTP server ready: http://{host}:{port}/")
    httpd.serve_forever()


async def start_relay_server0(host: str, port: int):
    async with websockets.serve(websocket_handler, host, port):
        print(f"WebSocket relay ready: ws://{host}:{port}")
        await asyncio.Future()

async def start_relay_server(host: str, port: int):
    # Increased max_size to 20 MB (20 * 1024 * 1024 bytes) to support larger payloads
    async with websockets.serve(websocket_handler, host, port, max_size=20 * 1024 * 1024):
        print(f"WebSocket relay ready: ws://{host}:{port}")
        await asyncio.Future()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Bible Song Pro LAN relay + local web server")
    parser.add_argument("--host", default="0.0.0.0", help="Listener host (default: 0.0.0.0)")
    parser.add_argument("--http-port", type=int, default=8000, help="HTTP port for the UI (default: 8000)")
    parser.add_argument("--relay-port", type=int, default=5511, help="WebSocket relay port (default: 5511)")
    args = parser.parse_args()

    http_thread = threading.Thread(target=start_http_server, args=(args.host, args.http_port), daemon=True)
    http_thread.start()

    try:
        await start_relay_server(args.host, args.relay_port)
    except KeyboardInterrupt:
        print("\nShutting down relay server...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExiting.")
