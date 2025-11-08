"""
Failed Task Exchange Manager
----------------------------
Manages the TTCC algorithm for processing failed tasks and reassigning them
to quantum resources.
"""

from typing import List, Optional, Callable
import simpy.core as sp

from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.task_queue import TaskQueue
from src.qschedulers.utils.ttcc import TTCCAlgorithm, TTCCAssignment
from src.logger_config import setup_logger

logger = setup_logger()


class FailedTaskExchangeManager:
    """
    Manages the exchange of failed tasks using the TTCC algorithm.
    
    When tasks fail, this manager:
    1. Collects failed tasks from the failed queue
    2. Runs the TTCC algorithm to find optimal reassignments
    3. Resubmits tasks to their newly assigned resources
    """
    
    def __init__(
        self,
        env: sp.Environment,
        qnodes: List[QuantumNode],
        failed_task_queue: TaskQueue,
        task_queue: TaskQueue,
        resubmit_callback: Optional[Callable[[QuantumTask, QuantumNode], None]] = None
    ):
        """
        Initialize the Failed Task Exchange Manager.
        
        Args:
            env: SimPy simulation environment
            qnodes: List of available quantum node resources
            failed_task_queue: Queue containing failed tasks
            task_queue: Main task queue for resubmitting tasks
            resubmit_callback: Optional callback function(task, qnode) to resubmit tasks
        """
        self.env = env
        self.qnodes = qnodes
        self.failed_task_queue = failed_task_queue
        self.task_queue = task_queue
        self.resubmit_callback = resubmit_callback
        self.ttcc_algorithm = TTCCAlgorithm(qnodes)
        self.logger = logger
        
        # Start the TTCC processing loop
        self.env.process(self._ttcc_processing_loop())
        
        self.logger.info("FailedTaskExchangeManager initialized")
    
    def _ttcc_processing_loop(self):
        """
        Main loop that periodically processes failed tasks using TTCC.
        
        This runs continuously, checking for failed tasks and processing them.
        """
        while True:
            # Wait a bit before checking (to allow tasks to accumulate)
            yield self.env.timeout(5.0)
            
            # Check if there are failed tasks
            if not self.failed_task_queue.is_empty():
                self.logger.info(
                    f"Processing {self.failed_task_queue.size()} failed tasks with TTCC"
                )
                self.process_failed_tasks()
    
    def process_failed_tasks(self) -> List[TTCCAssignment]:
        """
        Process all failed tasks in the queue using TTCC algorithm.
        
        Returns:
            List of assignments made by TTCC
        """
        # Collect all failed tasks
        failed_tasks = []
        while not self.failed_task_queue.is_empty():
            task = self.failed_task_queue.dequeue()
            if task:
                failed_tasks.append(task)
        
        if not failed_tasks:
            return []
        
        self.logger.info(f"Running TTCC on {len(failed_tasks)} failed tasks")
        
        # Run TTCC algorithm
        assignments = self.ttcc_algorithm.run(failed_tasks)
        
        # Process assignments
        for assignment in assignments:
            if assignment.resource is not None:
                # Resubmit task to assigned resource
                self._resubmit_task(assignment.task, assignment.resource)
            else:
                # Task goes to waiting list - re-enqueue to failed queue for later retry
                self.logger.debug(
                    f"Task {assignment.task.id} assigned to waiting list, "
                    "will be retried later"
                )
                self.failed_task_queue.enqueue(assignment.task)
        
        self.logger.info(
            f"TTCC processing complete: {len(assignments)} assignments made, "
            f"{sum(1 for a in assignments if a.resource is None)} to waiting list"
        )
        
        return assignments
    
    def _resubmit_task(self, task: QuantumTask, qnode: QuantumNode) -> None:
        """
        Resubmit a task to its newly assigned quantum node.
        
        Args:
            task: The task to resubmit
            qnode: The quantum node to resubmit to
        """
        self.logger.info(
            f"Resubmitting task {task.id} to {qnode.backend.name} "
            f"(previously failed: {task.last_failure_reason})"
        )
        
        # Clear previous failure reason (or keep it for tracking)
        # Optionally update task arrival time to current time
        task.arrival_time = self.env.now
        
        # Use callback if provided, otherwise enqueue to main task queue
        if self.resubmit_callback:
            self.resubmit_callback(task, qnode)
        else:
            # Default: enqueue to main task queue
            self.task_queue.enqueue(task)
    
    def trigger_immediate_processing(self) -> List[TTCCAssignment]:
        """
        Trigger immediate processing of failed tasks (useful when a task fails).
        
        Returns:
            List of assignments made
        """
        return self.process_failed_tasks()

