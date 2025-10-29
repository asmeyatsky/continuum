"""
Load Testing Framework for Continuum.

Provides comprehensive performance and scalability testing using Locust.
Tests API endpoints under various load conditions.
"""

import time
import logging
from typing import List, Dict, Any
from locust import HttpUser, task, between, TaskSet, constant_pacing
import pytest

logger = logging.getLogger(__name__)


class ContinuumLoadTest(TaskSet):
    """Load test scenarios for Continuum."""

    @task(3)
    def health_check(self):
        """Health check endpoint (frequently called)."""
        self.client.get("/health")

    @task(2)
    def submit_exploration(self):
        """Submit exploration request."""
        concepts = [
            "artificial intelligence",
            "machine learning",
            "quantum computing",
            "neural networks",
            "deep learning",
        ]
        payload = {"concept": concepts[self.client.env.random.randint(0, 4)]}
        self.client.post("/api/explorations", json=payload)

    @task(1)
    def get_exploration_status(self):
        """Get exploration status."""
        # Would need to track created exploration IDs
        exploration_id = "exp_12345"
        self.client.get(f"/api/explorations/{exploration_id}")

    @task(1)
    def search_knowledge_graph(self):
        """Search knowledge graph."""
        queries = ["AI", "learning", "models", "networks", "data"]
        query = queries[self.client.env.random.randint(0, 4)]
        self.client.get(f"/api/knowledge-graph/search", params={"q": query})

    @task(1)
    def get_node_details(self):
        """Get specific node details."""
        # Would need to track created node IDs
        node_id = "node_12345"
        self.client.get(f"/api/knowledge-graph/nodes/{node_id}")


class ContinuumUser(HttpUser):
    """Locust user model for Continuum."""

    tasks = [ContinuumLoadTest]
    wait_time = between(1, 3)

    def on_start(self):
        """Called when user starts."""
        logger.info(f"User {self.client_id} started")

    def on_stop(self):
        """Called when user stops."""
        logger.info(f"User {self.client_id} stopped")


# Pytest-based load test configuration
@pytest.fixture(scope="session")
def load_test_config() -> Dict[str, Any]:
    """Load test configuration."""
    return {
        "host": "http://localhost:8000",
        "users": 100,  # Number of concurrent users
        "spawn_rate": 10,  # Users spawned per second
        "duration": 300,  # Test duration in seconds
        "timeout": 30,  # Request timeout
        "thresholds": {
            "response_time_p95": 1000,  # 95th percentile < 1s
            "response_time_p99": 2000,  # 99th percentile < 2s
            "error_rate": 0.05,  # Error rate < 5%
            "requests_per_second": 100,  # Min 100 req/s
        },
    }


class LoadTestResult:
    """Stores and analyzes load test results."""

    def __init__(self):
        self.response_times: List[float] = []
        self.errors: int = 0
        self.success: int = 0
        self.start_time: float = 0
        self.end_time: float = 0

    def add_response(self, duration: float, success: bool = True):
        """Add response to results."""
        self.response_times.append(duration)
        if success:
            self.success += 1
        else:
            self.errors += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics from results."""
        if not self.response_times:
            return {}

        sorted_times = sorted(self.response_times)
        n = len(sorted_times)

        return {
            "total_requests": n + self.errors,
            "successful": self.success,
            "failed": self.errors,
            "error_rate": self.errors / (n + self.errors) if n + self.errors > 0 else 0,
            "min_response_time": min(sorted_times),
            "max_response_time": max(sorted_times),
            "avg_response_time": sum(sorted_times) / n,
            "p50_response_time": sorted_times[n // 2],
            "p95_response_time": sorted_times[int(n * 0.95)] if n > 20 else 0,
            "p99_response_time": sorted_times[int(n * 0.99)] if n > 100 else 0,
            "requests_per_second": n / (self.end_time - self.start_time) if self.end_time > self.start_time else 0,
        }

    def check_thresholds(
        self, thresholds: Dict[str, float]
    ) -> tuple[bool, List[str]]:
        """Check if results meet thresholds."""
        stats = self.get_stats()
        failures = []

        if stats.get("p95_response_time", float("inf")) > thresholds.get(
            "response_time_p95", float("inf")
        ):
            failures.append(
                f"P95 response time {stats['p95_response_time']:.0f}ms exceeds threshold {thresholds['response_time_p95']}ms"
            )

        if stats.get("p99_response_time", float("inf")) > thresholds.get(
            "response_time_p99", float("inf")
        ):
            failures.append(
                f"P99 response time {stats['p99_response_time']:.0f}ms exceeds threshold {thresholds['response_time_p99']}ms"
            )

        if stats.get("error_rate", 0) > thresholds.get("error_rate", 1):
            failures.append(
                f"Error rate {stats['error_rate']:.2%} exceeds threshold {thresholds['error_rate']:.2%}"
            )

        if stats.get("requests_per_second", 0) < thresholds.get(
            "requests_per_second", 0
        ):
            failures.append(
                f"Throughput {stats['requests_per_second']:.0f} req/s below threshold {thresholds['requests_per_second']} req/s"
            )

        return len(failures) == 0, failures


# Performance benchmarks for individual endpoints
class EndpointBenchmark:
    """Benchmark results for specific endpoint."""

    def __init__(self, name: str):
        self.name = name
        self.times: List[float] = []

    def add_timing(self, duration: float):
        """Add timing measurement."""
        self.times.append(duration)

    def get_stats(self) -> Dict[str, float]:
        """Get timing statistics."""
        if not self.times:
            return {}

        sorted_times = sorted(self.times)
        return {
            "min": min(sorted_times),
            "max": max(sorted_times),
            "avg": sum(sorted_times) / len(sorted_times),
            "p50": sorted_times[len(sorted_times) // 2],
            "p95": sorted_times[int(len(sorted_times) * 0.95)],
            "p99": sorted_times[int(len(sorted_times) * 0.99)],
        }


def run_baseline_benchmarks():
    """Run baseline performance benchmarks."""
    benchmarks = {
        "health": EndpointBenchmark("health"),
        "submit_exploration": EndpointBenchmark("submit_exploration"),
        "search_graph": EndpointBenchmark("search_graph"),
    }

    import requests

    host = "http://localhost:8000"

    # Health check benchmark (100 requests)
    for _ in range(100):
        start = time.time()
        requests.get(f"{host}/health")
        benchmarks["health"].add_timing((time.time() - start) * 1000)

    # Exploration submission benchmark (50 requests)
    for _ in range(50):
        start = time.time()
        requests.post(
            f"{host}/api/explorations",
            json={"concept": "machine learning"},
        )
        benchmarks["submit_exploration"].add_timing((time.time() - start) * 1000)

    # Search benchmark (100 requests)
    for _ in range(100):
        start = time.time()
        requests.get(f"{host}/api/knowledge-graph/search", params={"q": "AI"})
        benchmarks["search_graph"].add_timing((time.time() - start) * 1000)

    # Print results
    print("\n=== Baseline Performance Benchmarks ===\n")
    for name, bench in benchmarks.items():
        stats = bench.get_stats()
        print(f"{name}:")
        print(f"  Min:  {stats.get('min', 0):.2f}ms")
        print(f"  Max:  {stats.get('max', 0):.2f}ms")
        print(f"  Avg:  {stats.get('avg', 0):.2f}ms")
        print(f"  P95:  {stats.get('p95', 0):.2f}ms")
        print(f"  P99:  {stats.get('p99', 0):.2f}ms")
        print()

    return benchmarks


if __name__ == "__main__":
    # Run baseline benchmarks
    print("Running baseline performance benchmarks...")
    print("Make sure Continuum is running on http://localhost:8000")
    print()

    try:
        run_baseline_benchmarks()
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
