"""
Task Queue
---------
Defines the interface and implementations for quantum task queues.
"""

from abc import ABC, abstractmethod
from queue import Queue
from typing import List, Optional
import logging

from src.qschedulers.cloud.qtask import QuantumTask
from src.logger_config import setup_logger

logger = setup_logger()

class TaskQueue(ABC):
    """Abstract base class for task queues."""
    
    @abstractmethod
    def enqueue(self, task: QuantumTask) -> None:
        """Add a task to the queue."""
        pass
    
    @abstractmethod
    def enqueue_batch(self, tasks: List[QuantumTask]) -> None:
        """Add multiple tasks to the queue."""
        pass
    
    @abstractmethod
    def dequeue(self) -> Optional[QuantumTask]:
        """Remove and return a task from the queue."""
        pass
    
    @abstractmethod
    def dequeue_batch(self, batch_size: int) -> List[QuantumTask]:
        """Remove and return multiple tasks from the queue."""
        pass
    
    @abstractmethod
    def is_empty(self) -> bool:
        """Check if the queue is empty."""
        pass
    
    @abstractmethod
    def size(self) -> int:
        """Get the current size of the queue."""
        pass


class SimpleTaskQueue(TaskQueue):
    """A simple implementation of TaskQueue using Python's queue.Queue."""
    
    def __init__(self):
        self._queue: Queue = Queue()
        self.logger = logger
    
    def enqueue(self, task: QuantumTask) -> None:
        self._queue.put(task)
        self.logger.info(f"Task {task.id} enqueued")
    
    def enqueue_batch(self, tasks: List[QuantumTask]) -> None:
        for task in tasks:
            self.enqueue(task)
        self.logger.debug(f"Batch of {len(tasks)} tasks enqueued")
    
    def dequeue(self) -> Optional[QuantumTask]:
        if self.is_empty():
            return None
        task = self._queue.get()
        self.logger.debug(f"Task {task.id} dequeued")
        return task
    
    def dequeue_batch(self, batch_size: int) -> List[QuantumTask]:
        tasks = []
        for _ in range(min(batch_size, self.size())):
            task = self.dequeue()
            if task:
                tasks.append(task)
        if tasks:
            self.logger.info(f"Batch of {len(tasks)} tasks dequeued")
        return tasks
    
    def is_empty(self) -> bool:
        return self._queue.empty()
    
    def size(self) -> int:
        return self._queue.qsize()


class FailedTaskQueue(SimpleTaskQueue):
    """Specialized queue for tracking tasks that could not be completed."""

    def enqueue(self, task: QuantumTask) -> None:
        self._queue.put(task)
        self.logger.warning(f"Task {task.id} added to failed task queue")