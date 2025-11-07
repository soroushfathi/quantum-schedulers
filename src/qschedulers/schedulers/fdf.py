from typing import Any
from src.qschedulers.datasets.calibration_utils import get_gate_error_map
from .base import Scheduler
from src.logger_config import setup_logger

logger = setup_logger()

class FDFScheduler(Scheduler):
    """
    Fastest Duration First (FDF) Scheduler.
    Assigns each QTask to the QNode (backend) with the fastest average gate duration times.
    """

    def schedule(self, tasks: list[Any], qnodes: list[Any]) -> dict[str, Any]:
        logger.info(
            f"Scheduling {len(tasks)} tasks across {len(qnodes)} qnodes using FDF policy."
        )
        if not qnodes:
            logger.info("Initialized FDFScheduler with counter set to 0.")
            raise ValueError("No backends provided for scheduling.")

        assignments = []

        # Precompute average gate duration for each qnode
        qnode_avg_durations = []
        for qnode in qnodes:
            backend = qnode.backend
            err_map = get_gate_error_map(backend)
            durations = [v.get("length", 300e-9) for v in err_map.values() if v.get("length") is not None]
            avg_duration = sum(durations) / len(durations) if durations else 300e-9
            qnode_avg_durations.append(avg_duration)

        for task_id, task in enumerate(tasks):
            # Find qnode with fastest (smallest) average duration
            min_duration_idx = min(range(len(qnodes)), key=lambda i: qnode_avg_durations[i])
            best_qnode = qnodes[min_duration_idx]
            assignments.append((task_id, best_qnode))

        return {
            "assignments": assignments,
            "metadata": {
                "policy": "fastest_duration_first",
                "num_tasks": len(tasks),
                "num_backends": len(qnodes),
            },
        }