"""SOCForge Load Test Script.

Usage: python scripts/load_test.py --users 10 --duration 30
"""
import asyncio
import argparse
import time
import statistics
from datetime import datetime

import httpx


BASE_URL = "http://localhost:8000"


async def register_user(client: httpx.AsyncClient, idx: int) -> str:
    """Register a test user and return JWT token."""
    r = await client.post(f"{BASE_URL}/api/auth/register", json={
        "email": f"loadtest{idx}@test.com",
        "username": f"loadtest{idx}",
        "password": "LoadTest123!",
        "role": "analyst",
    })
    if r.status_code == 200:
        return r.json()["access_token"]
    # Try login if already registered
    r = await client.post(f"{BASE_URL}/api/auth/login", json={
        "username": f"loadtest{idx}",
        "password": "LoadTest123!",
    })
    return r.json()["access_token"]


async def run_simulation(client: httpx.AsyncClient, token: str) -> dict:
    """Run a simulation and return timing info."""
    start = time.perf_counter()
    r = await client.post(
        f"{BASE_URL}/api/simulation/start",
        json={"scenario": "ssh_brute_force", "intensity": "low", "duration_seconds": 10},
        headers={"Authorization": f"Bearer {token}"},
        timeout=60,
    )
    elapsed = time.perf_counter() - start
    return {"status": r.status_code, "time": elapsed}


async def query_endpoints(client: httpx.AsyncClient, token: str) -> list:
    """Hit read endpoints and return timing."""
    headers = {"Authorization": f"Bearer {token}"}
    results = []
    for path in ["/api/dashboard/stats", "/api/alerts/", "/api/events/", "/api/health"]:
        start = time.perf_counter()
        r = await client.get(f"{BASE_URL}{path}", headers=headers, timeout=10)
        elapsed = time.perf_counter() - start
        results.append({"path": path, "status": r.status_code, "time": elapsed})
    return results


async def worker(idx: int, duration: int, results: list):
    """Single worker loop."""
    async with httpx.AsyncClient() as client:
        token = await register_user(client, idx)
        end_time = time.time() + duration

        while time.time() < end_time:
            # Run simulation
            sim = await run_simulation(client, token)
            results.append({"type": "simulation", **sim})

            # Query endpoints
            queries = await query_endpoints(client, token)
            for q in queries:
                results.append({"type": "query", **q})


async def main(num_users: int, duration: int):
    print(f"\n{'='*60}")
    print(f"  SOCForge Load Test")
    print(f"  Concurrent users: {num_users}")
    print(f"  Duration: {duration}s")
    print(f"  Started: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    results: list = []
    tasks = [worker(i, duration, results) for i in range(num_users)]
    await asyncio.gather(*tasks, return_exceptions=True)

    # Analyze
    sim_results = [r for r in results if r["type"] == "simulation"]
    query_results = [r for r in results if r["type"] == "query"]

    sim_times = [r["time"] for r in sim_results]
    query_times = [r["time"] for r in query_results]
    errors = [r for r in results if r.get("status", 200) >= 400]

    print(f"\n{'='*60}")
    print(f"  RESULTS")
    print(f"{'='*60}")
    print(f"  Total requests:     {len(results)}")
    print(f"  Simulations run:    {len(sim_results)}")
    print(f"  Queries run:        {len(query_results)}")
    print(f"  Errors (4xx/5xx):   {len(errors)}")

    if sim_times:
        print(f"\n  Simulation Latency:")
        print(f"    Mean:   {statistics.mean(sim_times):.2f}s")
        print(f"    Median: {statistics.median(sim_times):.2f}s")
        print(f"    P95:    {sorted(sim_times)[int(len(sim_times)*0.95)]:.2f}s")
        print(f"    Max:    {max(sim_times):.2f}s")

    if query_times:
        print(f"\n  Query Latency:")
        print(f"    Mean:   {statistics.mean(query_times)*1000:.0f}ms")
        print(f"    Median: {statistics.median(query_times)*1000:.0f}ms")
        print(f"    P95:    {sorted(query_times)[int(len(query_times)*0.95)]*1000:.0f}ms")

    throughput = len(results) / duration
    print(f"\n  Throughput: {throughput:.1f} req/sec")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SOCForge Load Test")
    parser.add_argument("--users", type=int, default=5, help="Concurrent users")
    parser.add_argument("--duration", type=int, default=30, help="Test duration (sec)")
    args = parser.parse_args()
    asyncio.run(main(args.users, args.duration))
