#!/usr/bin/env python3
"""
Mah-a-Brain CLI -- interact with the agent from your terminal.

Usage:
    python3 cli.py health
    python3 cli.py chat "What is quantum computing?"
    python3 cli.py leach "Company sells red widgets" --source products
    python3 cli.py search "widgets"
    python3 cli.py cad
    python3 cli.py files
    python3 cli.py telemetry
"""

import argparse
import json
import sys
import asyncio

try:
    import httpx
except ImportError:
    print("httpx is required: pip install httpx")
    sys.exit(1)

DEFAULT_BASE = "http://localhost:8080"


def pp(data: dict) -> None:
    """Pretty-print JSON output."""
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_health(args: argparse.Namespace) -> None:
    r = httpx.get(f"{args.base}/api/health")
    pp(r.json())


def cmd_chat(args: argparse.Namespace) -> None:
    r = httpx.post(
        f"{args.base}/api/chat",
        json={"prompt": args.prompt, "api_key": args.api_key or ""},
        timeout=120,
    )
    data = r.json()
    print(data.get("response", data))
    if data.get("memory_enhanced"):
        print("\n(response enhanced with past memory)")


def cmd_leach(args: argparse.Namespace) -> None:
    r = httpx.post(
        f"{args.base}/api/memory/leach",
        json={"text": args.text, "source_name": args.source},
    )
    pp(r.json())


def cmd_search(args: argparse.Namespace) -> None:
    r = httpx.get(f"{args.base}/api/memory/search", params={"query": args.query, "n": args.n})
    data = r.json()
    if data.get("results"):
        for i, docs in enumerate(data["results"]):
            for doc in docs:
                print(f"  [{i+1}] {doc}")
    else:
        print("No results found.")


def cmd_cad(args: argparse.Namespace) -> None:
    r = httpx.post(f"{args.base}/api/cad/generate", timeout=60)
    data = r.json()
    pp(data)
    if data.get("download_url"):
        print(f"\nDownload: {args.base}{data['download_url']}")


def cmd_files(args: argparse.Namespace) -> None:
    r = httpx.get(f"{args.base}/api/cad/list")
    data = r.json()
    if not data["files"]:
        print("No CAD files yet.")
        return
    for f in data["files"]:
        size_kb = f["size_bytes"] / 1024
        print(f"  {f['filename']:30s}  {size_kb:6.1f} KB  {args.base}{f['download_url']}")
    print(f"\nTotal: {data['count']} file(s)")


def cmd_telemetry(args: argparse.Namespace) -> None:
    """Stream live telemetry to terminal."""
    import websockets  # type: ignore

    ws_url = args.base.replace("http://", "ws://").replace("https://", "wss://") + "/ws/telemetry"

    async def stream():
        async with websockets.connect(ws_url) as ws:
            print(f"Connected to {ws_url}. Press Ctrl+C to stop.\n")
            while True:
                msg = await ws.recv()
                print(msg)

    try:
        asyncio.run(stream())
    except KeyboardInterrupt:
        print("\nDisconnected.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Mah-a-Brain CLI")
    parser.add_argument("--base", default=DEFAULT_BASE, help="Server base URL")
    parser.add_argument("--api-key", default="", help="API key for billing")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("health", help="Check server health")

    p_chat = sub.add_parser("chat", help="Chat with the AI")
    p_chat.add_argument("prompt", help="Your message")

    p_leach = sub.add_parser("leach", help="Feed knowledge into memory")
    p_leach.add_argument("text", help="Text to store")
    p_leach.add_argument("--source", default="cli", help="Source label")

    p_search = sub.add_parser("search", help="Search memories")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("-n", type=int, default=5, help="Number of results")

    sub.add_parser("cad", help="Generate a CAD model")
    sub.add_parser("files", help="List generated CAD files with download links")
    sub.add_parser("telemetry", help="Stream live telemetry")

    args = parser.parse_args()
    commands = {
        "health": cmd_health,
        "chat": cmd_chat,
        "leach": cmd_leach,
        "search": cmd_search,
        "cad": cmd_cad,
        "files": cmd_files,
        "telemetry": cmd_telemetry,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
