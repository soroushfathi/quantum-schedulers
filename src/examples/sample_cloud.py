from mqt.bench import get_benchmark, BenchmarkLevel
import simpy.core as sp
import csv
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.schedulers import RoundRobinScheduler
from src.qschedulers.cloud.orchestrator import Orchestrator
from src.qschedulers.cloud.task_queue import FailedTaskQueue


if __name__ == "__main__":
    from qiskit_ibm_runtime.fake_provider import FakeHanoiV2, FakeBrisbane
    from mqt.bench import get_benchmark

    # Environment
    env = sp.Environment()

    # Backends wrapped in QNodes
    qnodes = [
        QuantumNode(env, FakeHanoiV2(), name="Hanoi"),
        QuantumNode(env, FakeBrisbane(), name="Brisbane"),
    ]

    # Example tasks (circuits with different arrival times)
    tasks = []
    # 1️⃣ Small circuits (fast → low waiting unless stacked)
    for i in range(2):
        tasks.append(
            QuantumTask(
                id=i,
                circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=5),
                arrival_time=0,  # both arrive together → waiting on same QNode
            )
        )

    # 2️⃣ Medium circuits (longer exec time → increases queueing)
    for i in range(2, 5):
        tasks.append(
            QuantumTask(
                id=i,
                circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=10),
                arrival_time=0 if i % 2 == 0 else 1,  # overlap arrivals
            )
        )

    # 3️⃣ Large circuits (should fail on small backends → "CircuitTooWide")
    for i in range(5, 7):
        tasks.append(
            QuantumTask(
                id=i,
                circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=30),
                arrival_time=1,  # arrives later but guaranteed to fail
            )
        )

    # 4️⃣ Late arrival small circuit (no wait, should succeed cleanly)
    tasks.append(
        QuantumTask(
            id=7,
            circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=5),
            arrival_time=5,  # arrives when backends are idle
        )
    )


    # Scheduler
    scheduler = RoundRobinScheduler()
    failed_q = FailedTaskQueue()
    orch = Orchestrator(env, scheduler, qnodes, failed_task_queue=failed_q)

    # Submit tasks to orchestrator
    orch.submit(tasks)

    # Run simulation
    env.run()

    results = orch.get_results()

    # Show results
    for r in results:
        print(r)

    if failed_q.size() > 0:
        print(f"\nFailed tasks in queue: {failed_q.size()}")
        preview = []
        while not failed_q.is_empty() and len(preview) < 5:
            t = failed_q.dequeue()
            if t:
                preview.append((t.id, getattr(t, 'last_failure_reason', None)))
        if preview:
            print("Preview of failures (task_id, reason):", preview)

    # -----------------------------
    # Export results to CSV
    # -----------------------------
    csv_path = "quantum_orchestrator_results.csv"
    if results:
        fieldnames = list(results[0].keys())
        with open(csv_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)

        print(f"\n✅ Saved results to {csv_path}")
    else:
        print("⚠️ No results to save.")