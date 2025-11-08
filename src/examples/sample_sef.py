from mqt.bench import get_benchmark, BenchmarkLevel
import simpy.core as sp
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.schedulers.sef import SEFScheduler
from src.qschedulers.cloud.orchestrator import Orchestrator
from src.qschedulers.cloud.task_queue import FailedTaskQueue

if __name__ == "__main__":
    from qiskit_ibm_runtime.fake_provider import FakeHanoiV2, FakeBrisbane

    # Environment
    env = sp.Environment()

    # Backends wrapped in QNodes
    qnodes = [
        QuantumNode(env, FakeHanoiV2(), name="Hanoi"),
        QuantumNode(env, FakeBrisbane(), name="Brisbane"),
    ]

    # Example tasks (circuits with different arrival times)
    tasks = [
        QuantumTask(
            id=0,
            circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=5),
            arrival_time=0,
        ),
        QuantumTask(
            id=1,
            circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=10),
            arrival_time=1,
        ),
        QuantumTask(
            id=2,
            circuit=get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=30),
            arrival_time=1,
        ),
        QuantumTask(
            id=3,
            circuit=get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=5),
            arrival_time=5,
        ),
    ]

    # Scheduler
    scheduler = SEFScheduler()
    failed_q = FailedTaskQueue()
    orch = Orchestrator(env, scheduler, qnodes, failed_task_queue=failed_q)

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
