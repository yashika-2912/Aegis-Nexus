"""Launch all Aegis Shop microservices."""
import os
import subprocess
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parent

SERVICES = [
    ("User Service", [sys.executable, "-m", "uvicorn", "services.user_service:app", "--host", "0.0.0.0", "--port", "8001"]),
    ("Product Service", [sys.executable, "-m", "uvicorn", "services.product_service:app", "--host", "0.0.0.0", "--port", "8002"]),
    ("Order Service", [sys.executable, "-m", "uvicorn", "services.order_service:app", "--host", "0.0.0.0", "--port", "8003"]),
    ("Payment Service", [sys.executable, "-m", "uvicorn", "services.payment_service:app", "--host", "0.0.0.0", "--port", "8004"]),
    ("API Gateway", [sys.executable, "-m", "uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]),
]

if __name__ == "__main__":
    procs = []
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BACKEND)
    for name, cmd in SERVICES:
        print(f"Starting {name}...")
        p = subprocess.Popen(cmd, cwd=str(BACKEND), env=env)
        procs.append((name, p))
        time.sleep(0.5)

    print("\nAll Aegis Shop services running:")
    print("  Gateway:  http://localhost:8000")
    print("  User:     http://localhost:8001")
    print("  Product:  http://localhost:8002")
    print("  Order:    http://localhost:8003")
    print("  Payment:  http://localhost:8004")
    print("\nPress Ctrl+C to stop all services.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping services...")
        for name, p in procs:
            p.terminate()
            print(f"  Stopped {name}")
