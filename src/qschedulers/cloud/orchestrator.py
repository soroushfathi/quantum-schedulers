"""
Orchestrator
------------
Coordinates tasks, schedulers, and quantum nodes inside a qsimpy environment.
"""

import simpy.core as sp
from qiskit import transpile
from typing import List, Optional

from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.schedulers.base import Scheduler
from src.qschedulers.datasets.calibration_utils import get_gate_error_map
from src.qschedulers.evaluation.metrics import estimate_fidelity_and_time
from src.qschedulers.cloud.task_queue import TaskQueue, SimpleTaskQueue
from src.logger_config import setup_logger

logger = setup_logger()

class Orchestrator:
    """
    Queue-based orchestrator that processes tasks in batches periodically.
    """
    def __init__(
        self,
        env: sp.Environment,
        scheduler: Scheduler,
        qnodes: List[QuantumNode],
        task_queue: Optional[TaskQueue] = None,
        shots: int = 1024,
        batch_size: int = 5,
        schedule_interval: float = 10.0
    ):
        self.env = env
        self.scheduler = scheduler
        self.qnodes = qnodes
        self.task_queue = task_queue or SimpleTaskQueue()
        self.shots = shots
        self.batch_size = batch_size
        self.schedule_interval = schedule_interval
        self.results = []
        
        # Start the scheduling process
        self.env.process(self._scheduling_loop())
        logger.info("Orchestrator initialized with batch processing")

    def submit(self, tasks: List[QuantumTask]) -> None:
        """Submit tasks by spawning arrival processes for each task.

        Each task will be enqueued at its absolute arrival_time (in env time).
        This models real-world arrivals and allows measuring waiting time accurately.
        """
        for task in tasks:
            # spawn an arrival process per task so it is enqueued at the correct time
            self.env.process(self._task_arrival_process(task))

    def _task_arrival_process(self, task: QuantumTask):
        """Process that waits until the task's absolute arrival time and enqueues it."""
        delay = max(0.0, task.arrival_time - self.env.now)
        if delay > 0:
            yield self.env.timeout(delay)
        # record actual enqueue time for accurate waiting-time measurement
        task.enqueue_time = self.env.now
        self.task_queue.enqueue(task)
        logger.info(f"Task {task.id} arrived at t={self.env.now} and enqueued")
    
    def _scheduling_loop(self):
        """Main scheduling loop that processes tasks in batches periodically."""
        while True:
            # Wait for the next scheduling interval
            yield self.env.timeout(self.schedule_interval)
            
            # Get a batch of tasks
            print(f'size before deque {self.task_queue.size()}.')
            tasks = self.task_queue.dequeue_batch(self.batch_size)
            print(f'size after deque {self.task_queue.size()}.')
            if not tasks:
                logger.debug("No tasks to schedule in this interval")
                continue
                
            logger.info(f"Processing batch of {len(tasks)} tasks")
            
            # Schedule the batch
            try:
                result = self.scheduler.schedule(tasks, self.qnodes)
                assignments = result["assignments"]
                
                # Process assignments
                for task_id, qnode in assignments:
                    task = tasks[task_id]
                    self.env.process(self._run_task(task, qnode))
                    logger.debug(f"Task {task.id} assigned to {qnode.backend.name if qnode else 'None'}")
                    
            except Exception as e:
                logger.error(f"Error scheduling batch: {str(e)}")
                # Return tasks to queue in case of error
                self.task_queue.enqueue_batch(tasks)

    def _run_task(self, task: QuantumTask, qnode: Optional[QuantumNode]):
        """Execute a single task on its assigned quantum node.

        Assumes task has already been enqueued (i.e., arrived). The enqueue time
        is used as the arrival time for waiting/turnaround calculations.
        """
        # arrival is the time the task was enqueued; fall back to task.arrival_time
        arrival = getattr(task, 'enqueue_time', task.arrival_time)

        if not qnode:
            logger.warning(f"Task {task.id} failed: No quantum node assigned")
            self._record_failed_task(task, arrival)
            return None

        with qnode.request() as req:
            yield req
            start = self.env.now
            waiting_time = start - arrival

            status = "success"
            error_message = None

            # Estimate exec time as service time
            try:
                logger.debug(f"Transpiling task {task.id} for {qnode.backend.name}")
                tqc = transpile(
                    task.circuit, backend=qnode.backend, optimization_level=3
                )

                err_map = get_gate_error_map(qnode.backend)
                fidelity, exec_time, swaps = estimate_fidelity_and_time(
                    tqc, qnode.backend, err_map, shots=self.shots
                )
                service_time = exec_time
                logger.debug(f"Task {task.id} transpiled successfully. Expected execution time: {exec_time}")
            except Exception as e:
                error_message = str(e)
                status = "failed"
                fidelity, exec_time, swaps = None, None, None
                service_time = 1.0
                logger.error(f"Error transpiling task {task.id}: {error_message}")

            # Simulate execution time
            yield self.env.timeout(service_time)

            finish = self.env.now
            turnaround_time = finish - arrival

            self._record_task_result(
                task, qnode, status, error_message,
                arrival, start, finish, waiting_time,
                turnaround_time, fidelity, exec_time, swaps
            )
            
            logger.info(f"Task {task.id} completed with status {status}")

    def _record_failed_task(self, task: QuantumTask, arrival: float) -> None:
        """Record results for a failed task."""
        self.results.append({
            "task_id": task.id,
            "backend": "",
            "status": "failed",
            "message": "No quantum node available",
            "arrival_time": arrival,
            "start_time": -1,
            "finish_time": -1,
            "waiting_time": -1,
            "turnaround_time": -1,
            "fidelity": -1,
            "exec_time_est": -1,
            "swap_count": -1,
        })

    def _record_task_result(
        self, task: QuantumTask, qnode: QuantumNode,
        status: str, error_message: Optional[str],
        arrival: float, start: float, finish: float,
        waiting_time: float, turnaround_time: float,
        fidelity: Optional[float], exec_time: Optional[float],
        swaps: Optional[int]
    ) -> None:
        """Record the results of a completed task."""
        self.results.append({
            "task_id": task.id,
            "backend": qnode.backend.name,
            "status": status,
            "message": error_message,
                    "arrival_time": arrival,
                    "start_time": start,
                    "finish_time": finish,
                    "waiting_time": waiting_time,
                    "turnaround_time": turnaround_time,
                    "fidelity": fidelity,
                    "exec_time_est": exec_time,
                    "swap_count": swaps,
                }
            )

    def get_results(self):
        return self.results
