"""
Unit tests for the Top Trading Cycles and Chains (TTCC) algorithm.
"""

import unittest
import unittest.mock
from unittest.mock import Mock, MagicMock
from qiskit import QuantumCircuit

from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.task_queue import SimpleTaskQueue, FailedTaskQueue
from src.qschedulers.utils.ttcc import TTCCAlgorithm, TTCCAssignment, TTCCState
from src.qschedulers.utils.compatibility import (
    is_task_compatible_with_resource,
    get_compatible_resources,
    get_task_preference_list
)
import simpy


class TestTTCCCycleDetection(unittest.TestCase):
    """Test cycle detection in TTCC algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock backends
        self.backend1 = Mock()
        self.backend1.name = "backend1"
        self.backend1.configuration.return_value.n_qubits = 5
        
        self.backend2 = Mock()
        self.backend2.name = "backend2"
        self.backend2.configuration.return_value.n_qubits = 5
        
        self.backend3 = Mock()
        self.backend3.name = "backend3"
        self.backend3.configuration.return_value.n_qubits = 5
        
        # Create quantum nodes
        self.qnode1 = Mock(spec=QuantumNode)
        self.qnode1.backend = self.backend1
        
        self.qnode2 = Mock(spec=QuantumNode)
        self.qnode2.backend = self.backend2
        
        self.qnode3 = Mock(spec=QuantumNode)
        self.qnode3.backend = self.backend3
        
        self.qnodes = [self.qnode1, self.qnode2, self.qnode3]
        
        # Create test circuits
        self.circuit1 = QuantumCircuit(3)
        self.circuit2 = QuantumCircuit(3)
        self.circuit3 = QuantumCircuit(3)
        
        # Create tasks
        self.task1 = QuantumTask(id=1, circuit=self.circuit1, priority=1)
        self.task2 = QuantumTask(id=2, circuit=self.circuit2, priority=2)
        self.task3 = QuantumTask(id=3, circuit=self.circuit3, priority=3)
    
    def test_find_simple_cycle(self):
        """Test detection of a simple 3-task cycle."""
        algorithm = TTCCAlgorithm(self.qnodes)
        
        # Create a state with a cycle: task1 -> qnode1 -> task2 -> qnode2 -> task3 -> qnode3 -> task1
        state = TTCCState(
            task_to_resource={
                self.task1: self.qnode1,
                self.task2: self.qnode2,
                self.task3: self.qnode3
            },
            resource_to_task={
                self.qnode1: self.task2,
                self.qnode2: self.task3,
                self.qnode3: self.task1
            },
            assigned_tasks=set(),
            waiting_list_tasks=set()
        )
        
        tasks = [self.task1, self.task2, self.task3]
        cycle = algorithm._find_cycle(tasks, state)
        
        self.assertIsNotNone(cycle, "Should find a cycle")
        self.assertEqual(len(cycle), 4, "Cycle should include all 3 tasks plus start")  # Includes start task twice
        # Check that all tasks are in the cycle
        self.assertIn(self.task1, cycle)
        self.assertIn(self.task2, cycle)
        self.assertIn(self.task3, cycle)
    
    def test_find_no_cycle(self):
        """Test that no cycle is found when tasks point to free resources."""
        algorithm = TTCCAlgorithm(self.qnodes)
        
        # Tasks point to free resources (no cycle)
        state = TTCCState(
            task_to_resource={
                self.task1: self.qnode1,
                self.task2: self.qnode2,
                self.task3: self.qnode3
            },
            resource_to_task={
                self.qnode1: None,  # Free
                self.qnode2: None,  # Free
                self.qnode3: None   # Free
            },
            assigned_tasks=set(),
            waiting_list_tasks=set()
        )
        
        tasks = [self.task1, self.task2, self.task3]
        cycle = algorithm._find_cycle(tasks, state)
        
        self.assertIsNone(cycle, "Should not find a cycle when resources are free")
    
    def test_find_self_cycle(self):
        """Test detection of a self-cycle (task points to resource that points back to itself)."""
        algorithm = TTCCAlgorithm(self.qnodes)
        
        # Task1 points to qnode1, which is owned by task1 (self-cycle)
        state = TTCCState(
            task_to_resource={
                self.task1: self.qnode1
            },
            resource_to_task={
                self.qnode1: self.task1
            },
            assigned_tasks=set(),
            waiting_list_tasks=set()
        )
        
        tasks = [self.task1]
        cycle = algorithm._find_cycle(tasks, state)
        
        self.assertIsNotNone(cycle, "Should find a self-cycle")
        self.assertIn(self.task1, cycle)


class TestTTCCChainSelection(unittest.TestCase):
    """Test chain selection in TTCC algorithm."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock backends
        self.backend1 = Mock()
        self.backend1.name = "backend1"
        self.backend1.configuration.return_value.n_qubits = 5
        
        self.backend2 = Mock()
        self.backend2.name = "backend2"
        self.backend2.configuration.return_value.n_qubits = 5
        
        # Create quantum nodes
        self.qnode1 = Mock(spec=QuantumNode)
        self.qnode1.backend = self.backend1
        
        self.qnode2 = Mock(spec=QuantumNode)
        self.qnode2.backend = self.backend2
        
        self.qnodes = [self.qnode1, self.qnode2]
        
        # Create test circuits
        self.circuit1 = QuantumCircuit(3)
        self.circuit2 = QuantumCircuit(3)
        self.circuit3 = QuantumCircuit(3)
        
        # Create tasks with different priorities
        self.task1 = QuantumTask(id=1, circuit=self.circuit1, priority=1)  # Lowest priority
        self.task2 = QuantumTask(id=2, circuit=self.circuit2, priority=2)
        self.task3 = QuantumTask(id=3, circuit=self.circuit3, priority=3)  # Highest priority
    
    def test_find_chain_highest_priority_first(self):
        """Test that chain selection starts with highest priority task (rule e)."""
        algorithm = TTCCAlgorithm(self.qnodes)
        
        # Create a chain: task3 (highest priority) -> qnode1 -> task2 -> qnode2 -> task1 -> None
        state = TTCCState(
            task_to_resource={
                self.task1: None,  # Points to waiting list
                self.task2: self.qnode2,
                self.task3: self.qnode1
            },
            resource_to_task={
                self.qnode1: self.task2,
                self.qnode2: self.task1
            },
            assigned_tasks=set(),
            waiting_list_tasks=set()
        )
        
        tasks = [self.task1, self.task2, self.task3]
        chain = algorithm._find_chain(tasks, state)
        
        self.assertIsNotNone(chain, "Should find a chain")
        # Chain should start with highest priority task (task3)
        self.assertEqual(chain[0], self.task3, "Chain should start with highest priority task")
    
    def test_find_chain_ending_at_waiting_list(self):
        """Test chain that ends at waiting list."""
        algorithm = TTCCAlgorithm(self.qnodes)
        
        # Chain: task1 -> qnode1 -> task2 -> None (waiting list)
        state = TTCCState(
            task_to_resource={
                self.task1: self.qnode1,
                self.task2: None  # Points to waiting list
            },
            resource_to_task={
                self.qnode1: self.task2
            },
            assigned_tasks=set(),
            waiting_list_tasks=set()
        )
        
        tasks = [self.task1, self.task2]
        chain = algorithm._find_chain(tasks, state)
        
        self.assertIsNotNone(chain, "Should find a chain")
        self.assertEqual(len(chain), 2, "Chain should have 2 tasks")
        self.assertEqual(chain[-1], self.task2, "Last task should be the one pointing to waiting list")
    
    def test_find_chain_ending_at_free_resource(self):
        """Test chain that ends at a free resource."""
        algorithm = TTCCAlgorithm(self.qnodes)
        
        # Chain: task1 -> qnode1 -> task2 -> qnode2 (free)
        state = TTCCState(
            task_to_resource={
                self.task1: self.qnode1,
                self.task2: self.qnode2
            },
            resource_to_task={
                self.qnode1: self.task2,
                self.qnode2: None  # Free resource
            },
            assigned_tasks=set(),
            waiting_list_tasks=set()
        )
        
        tasks = [self.task1, self.task2]
        chain = algorithm._find_chain(tasks, state)
        
        self.assertIsNotNone(chain, "Should find a chain")
        self.assertEqual(len(chain), 2, "Chain should have 2 tasks")
        self.assertEqual(chain[-1], self.task2, "Last task should point to free resource")


class TestTTCCFullAlgorithm(unittest.TestCase):
    """Test the full TTCC algorithm execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock backends with different qubit counts
        self.backend1 = Mock()
        self.backend1.name = "backend1"
        self.backend1.configuration.return_value.n_qubits = 5
        
        self.backend2 = Mock()
        self.backend2.name = "backend2"
        self.backend2.configuration.return_value.n_qubits = 3
        
        # Create quantum nodes
        self.qnode1 = Mock(spec=QuantumNode)
        self.qnode1.backend = self.backend1
        
        self.qnode2 = Mock(spec=QuantumNode)
        self.qnode2.backend = self.backend2
        
        self.qnodes = [self.qnode1, self.qnode2]
        
        # Create test circuits
        self.circuit1 = QuantumCircuit(3)
        self.circuit2 = QuantumCircuit(3)
        
        # Create tasks
        self.task1 = QuantumTask(id=1, circuit=self.circuit1, priority=1)
        self.task2 = QuantumTask(id=2, circuit=self.circuit2, priority=2)
    
    def test_ttcc_with_cycle(self):
        """Test TTCC algorithm with a cycle scenario."""
        # Mock compatibility to make both tasks compatible with both resources
        with unittest.mock.patch(
            'src.qschedulers.utils.compatibility.get_task_preference_list'
        ) as mock_pref:
            # Both tasks prefer qnode1, then qnode2
            mock_pref.return_value = [self.qnode1, self.qnode2]
            
            algorithm = TTCCAlgorithm(self.qnodes)
            
            # Create a scenario where we can form a cycle
            # This is simplified - in practice, the algorithm will set up preferences
            failed_tasks = [self.task1, self.task2]
            
            # Run algorithm
            assignments = algorithm.run(failed_tasks)
            
            # Should get assignments for both tasks
            self.assertEqual(len(assignments), 2, "Should assign both tasks")
            
            # Check that each task is assigned
            assigned_task_ids = {a.task.id for a in assignments}
            self.assertEqual(assigned_task_ids, {1, 2}, "Both tasks should be assigned")
    
    def test_ttcc_empty_input(self):
        """Test TTCC with empty input."""
        algorithm = TTCCAlgorithm(self.qnodes)
        assignments = algorithm.run([])
        self.assertEqual(len(assignments), 0, "Should return empty list for empty input")
    
    def test_ttcc_single_task(self):
        """Test TTCC with a single task."""
        with unittest.mock.patch(
            'src.qschedulers.utils.compatibility.get_task_preference_list'
        ) as mock_pref:
            mock_pref.return_value = [self.qnode1]
            
            algorithm = TTCCAlgorithm(self.qnodes)
            assignments = algorithm.run([self.task1])
            
            # Should get one assignment
            self.assertEqual(len(assignments), 1, "Should assign the single task")
            self.assertEqual(assignments[0].task.id, 1, "Should assign task1")


class TestCompatibility(unittest.TestCase):
    """Test compatibility checking functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.backend = Mock()
        self.backend.name = "test_backend"
        self.backend.configuration.return_value.n_qubits = 5
        
        self.qnode = Mock(spec=QuantumNode)
        self.qnode.backend = self.backend
        
        self.circuit = QuantumCircuit(3)
        self.task = QuantumTask(id=1, circuit=self.circuit)
    
    def test_compatibility_sufficient_qubits(self):
        """Test compatibility when node has sufficient qubits."""
        with unittest.mock.patch('qiskit.transpile') as mock_transpile:
            mock_transpile.return_value = QuantumCircuit(3)
            
            from src.qschedulers.utils.compatibility import is_task_compatible_with_resource
            result = is_task_compatible_with_resource(self.task, self.qnode)
            
            self.assertTrue(result, "Should be compatible when qubits are sufficient")
    
    def test_compatibility_insufficient_qubits(self):
        """Test compatibility when node has insufficient qubits."""
        # Create circuit requiring more qubits than available
        large_circuit = QuantumCircuit(10)
        large_task = QuantumTask(id=2, circuit=large_circuit)
        
        from src.qschedulers.utils.compatibility import is_task_compatible_with_resource
        result = is_task_compatible_with_resource(large_task, self.qnode)
        
        self.assertFalse(result, "Should not be compatible when qubits are insufficient")


class TestTTCCFailureCount(unittest.TestCase):
    """Test the 3-failure rule: tasks that fail 3 times in TTCC move to main queue."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create mock backend
        self.backend = Mock()
        self.backend.name = "test_backend"
        self.backend.configuration.return_value.n_qubits = 5
        
        # Create quantum node
        self.qnode = Mock(spec=QuantumNode)
        self.qnode.backend = self.backend
        
        self.qnodes = [self.qnode]
        
        # Create test circuit
        self.circuit = QuantumCircuit(3)
        
        # Create SimPy environment
        self.env = simpy.Environment()
        
        # Create queues
        self.failed_queue = FailedTaskQueue()
        self.main_queue = SimpleTaskQueue()
    
    def test_task_moves_to_main_queue_after_3_failures(self):
        """Test that a task moves to main queue after 3 TTCC failures."""
        from src.qschedulers.cloud.failed_task_exchange_manager import FailedTaskExchangeManager
        
        # Create task with 2 previous failures
        task = QuantumTask(id=1, circuit=self.circuit, ttcc_failure_count=2)
        
        # Add task to failed queue
        self.failed_queue.enqueue(task)
        
        # Create manager
        manager = FailedTaskExchangeManager(
            env=self.env,
            qnodes=self.qnodes,
            failed_task_queue=self.failed_queue,
            task_queue=self.main_queue
        )
        
        # Mock TTCC to return waiting list assignment (no resource)
        with unittest.mock.patch.object(manager.ttcc_algorithm, 'run') as mock_run:
            # TTCC returns assignment to waiting list (resource=None)
            mock_run.return_value = [TTCCAssignment(task=task, resource=None)]
            
            # Process failed tasks
            assignments = manager.process_failed_tasks()
            
            # Task should have failure count incremented to 3, then reset to 0 after moving to main queue
            self.assertEqual(task.ttcc_failure_count, 0, "Count should be reset after moving to main queue")
            
            # Verify task is not in failed queue (should be empty or not contain this task)
            # The task should have been moved to main queue
            failed_queue_tasks = []
            while not self.failed_queue.is_empty():
                failed_queue_tasks.append(self.failed_queue.dequeue())
            self.assertNotIn(task, failed_queue_tasks, "Task should not be in failed queue after 3 failures")
    
    def test_task_stays_in_failed_queue_before_3_failures(self):
        """Test that a task stays in failed queue if failure count < 3."""
        from src.qschedulers.cloud.failed_task_exchange_manager import FailedTaskExchangeManager
        
        # Create task with 1 previous failure
        task = QuantumTask(id=1, circuit=self.circuit, ttcc_failure_count=1)
        
        # Add task to failed queue
        self.failed_queue.enqueue(task)
        initial_size = self.failed_queue.size()
        
        # Create manager
        manager = FailedTaskExchangeManager(
            env=self.env,
            qnodes=self.qnodes,
            failed_task_queue=self.failed_queue,
            task_queue=self.main_queue
        )
        
        # Mock TTCC to return waiting list assignment
        with unittest.mock.patch.object(manager.ttcc_algorithm, 'run') as mock_run:
            mock_run.return_value = [TTCCAssignment(task=task, resource=None)]
            
            # Process failed tasks
            manager.process_failed_tasks()
            
            # Task should have failure count incremented to 2
            self.assertEqual(task.ttcc_failure_count, 2, "Failure count should be 2")
            
            # Task should still be in failed queue (not moved to main queue)
            # We verify by checking the count is not reset
            self.assertNotEqual(task.ttcc_failure_count, 0, "Count should not be reset")
    
    def test_task_resets_count_on_successful_assignment(self):
        """Test that task failure count resets when successfully assigned."""
        from src.qschedulers.cloud.failed_task_exchange_manager import FailedTaskExchangeManager
        
        # Create task with 2 previous failures
        task = QuantumTask(id=1, circuit=self.circuit, ttcc_failure_count=2)
        
        # Add task to failed queue
        self.failed_queue.enqueue(task)
        
        # Create manager
        manager = FailedTaskExchangeManager(
            env=self.env,
            qnodes=self.qnodes,
            failed_task_queue=self.failed_queue,
            task_queue=self.main_queue
        )
        
        # Mock TTCC to return successful assignment
        with unittest.mock.patch.object(manager.ttcc_algorithm, 'run') as mock_run:
            mock_run.return_value = [TTCCAssignment(task=task, resource=self.qnode)]
            
            # Process failed tasks
            manager.process_failed_tasks()
            
            # Task should have failure count reset to 0
            self.assertEqual(task.ttcc_failure_count, 0, "Failure count should be reset on successful assignment")
    
    def test_task_failure_count_tracking(self):
        """Test that failure count increments correctly through multiple TTCC cycles."""
        from src.qschedulers.cloud.failed_task_exchange_manager import FailedTaskExchangeManager
        
        # Create fresh task
        task = QuantumTask(id=1, circuit=self.circuit, ttcc_failure_count=0)
        
        # Create manager
        manager = FailedTaskExchangeManager(
            env=self.env,
            qnodes=self.qnodes,
            failed_task_queue=self.failed_queue,
            task_queue=self.main_queue
        )
        
        # First failure
        self.failed_queue.enqueue(task)
        with unittest.mock.patch.object(manager.ttcc_algorithm, 'run') as mock_run:
            mock_run.return_value = [TTCCAssignment(task=task, resource=None)]
            manager.process_failed_tasks()
            self.assertEqual(task.ttcc_failure_count, 1, "First failure should set count to 1")
        
        # Second failure
        self.failed_queue.enqueue(task)
        with unittest.mock.patch.object(manager.ttcc_algorithm, 'run') as mock_run:
            mock_run.return_value = [TTCCAssignment(task=task, resource=None)]
            manager.process_failed_tasks()
            self.assertEqual(task.ttcc_failure_count, 2, "Second failure should set count to 2")
        
        # Third failure - should move to main queue
        self.failed_queue.enqueue(task)
        with unittest.mock.patch.object(manager.ttcc_algorithm, 'run') as mock_run:
            mock_run.return_value = [TTCCAssignment(task=task, resource=None)]
            manager.process_failed_tasks()
            # Count should be 0 after moving to main queue
            self.assertEqual(task.ttcc_failure_count, 0, "Count should reset after 3rd failure moves to main queue")


if __name__ == '__main__':
    unittest.main()

