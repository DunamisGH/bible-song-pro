#!/usr/bin/env python3
"""Start the Bible Song Pro LAN server and configure Tailscale Funnel."""

import shutil
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FUNNEL_ROUTES = (
    ("443", "http://127.0.0.1:8000"),
    ("10000", "http://127.0.0.1:5511"),
)


def main() -> int:
    tailscale = shutil.which("tailscale") or shutil.which("tailscale.exe")
    if not tailscale:
        print("Error: Tailscale CLI was not found. Install/start Tailscale, then try again.")
        return 1

    server = subprocess.Popen(
        [sys.executable, str(ROOT / "lan_server.py")],
        cwd=ROOT,
        creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
    )

    try:
        # Give the local HTTP and WebSocket listeners time to start before Funnel checks them.
        time.sleep(1)
        if server.poll() is not None:
            print("Error: lan_server.py exited before it was ready.")
            return int(server.returncode or 1)

        for public_port, target in FUNNEL_ROUTES:
            command = [tailscale, "funnel", "--bg", f"--https={public_port}", target]
            print(f"Configuring Funnel port {public_port} -> {target}...")
            result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
            if result.stdout:
                print(result.stdout.strip())
            if result.returncode != 0:
                if result.stderr:
                    print(result.stderr.strip())
                print("Funnel setup failed. Check that Tailscale is connected and Funnel is enabled.")
                return result.returncode

        print("\nBible Song Pro server and Funnel are running.")
        print("In Remote Show settings, use port 443 and relay port 10000.")
        print("Press Ctrl+C to stop the local server. Funnel routes remain configured in Tailscale.")
        while server.poll() is None:
            time.sleep(1)
        print(f"\nThe local server stopped with exit code {server.returncode}.")
        return int(server.returncode or 0)
    except KeyboardInterrupt:
        print("\nStopping the local server...")
        return 0
    finally:
        if server.poll() is None:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()


if __name__ == "__main__":
    raise SystemExit(main())
