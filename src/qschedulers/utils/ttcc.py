"""
Top Trading Cycles and Chains (TTCC) Algorithm
-----------------------------------------------
Implementation of the TTCC algorithm for matching failed tasks (patients) 
with quantum resources (donor kidneys).

The algorithm proceeds in iterations:
1. Each task points to its most preferred compatible resource
2. If a cycle is found, assign resources to all tasks in the cycle
3. If no cycle, find a chain starting with highest priority task
4. Assign all tasks in the chain, add last task to waiting list
5. Repeat until queue is empty
"""

from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass

from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.utils.compatibility import get_task_preference_list
from src.logger_config import setup_logger

logger = setup_logger()


# Special marker for "waiting list" (no resource available)
WAITING_LIST = "WAITING_LIST"


@dataclass
class TTCCAssignment:
    """Represents an assignment of a task to a resource."""
    task: QuantumTask
    resource: Optional[QuantumNode]  # None means assigned to waiting list
    

@dataclass
class TTCCState:
    """Internal state for TTCC algorithm."""
    # Mapping from task to its current preferred resource
    task_to_resource: Dict[QuantumTask, Optional[QuantumNode]]
    # Mapping from resource to its current owner (task)
    resource_to_task: Dict[QuantumNode, Optional[QuantumTask]]
    # Tasks that have been assigned and should be removed
    assigned_tasks: Set[QuantumTask]
    # Tasks assigned to waiting list
    waiting_list_tasks: Set[QuantumTask]


class TTCCAlgorithm:
    """
    Top Trading Cycles and Chains algorithm implementation.
    
    This class implements the TTCC algorithm for matching failed tasks
    with quantum resources.
    """
    
    def __init__(self, qnodes: List[QuantumNode]):
        """
        Initialize the TTCC algorithm.
        
        Args:
            qnodes: List of available quantum node resources
        """
        self.qnodes = qnodes
        self.logger = logger
    
    def run(
        self, 
        failed_tasks: List[QuantumTask]
    ) -> List[TTCCAssignment]:
        """
        Run the TTCC algorithm on a list of failed tasks.
        
        Args:
            failed_tasks: List of failed tasks to match with resources
            
        Returns:
            List of assignments (task -> resource or waiting list)
        """
        if not failed_tasks:
            return []
        
        self.logger.info(f"Running TTCC algorithm on {len(failed_tasks)} failed tasks")
        
        # Initialize state
        state = TTCCState(
            task_to_resource={},
            resource_to_task={qnode: None for qnode in self.qnodes},
            assigned_tasks=set(),
            waiting_list_tasks=set()
        )
        
        # Remaining tasks to process
        remaining_tasks = list(failed_tasks)
        assignments = []
        
        iteration = 0
        while remaining_tasks:
            iteration += 1
            self.logger.debug(f"TTCC iteration {iteration}: {len(remaining_tasks)} tasks remaining")
            
            # Step h.1: Each task points to its most preferred compatible resource
            self._update_preferences(remaining_tasks, state)
            
            # Step h.2: Check for cycles
            cycle = self._find_cycle(remaining_tasks, state)
            
            if cycle:
                # Assign all tasks in the cycle
                self.logger.debug(f"Found cycle of length {len(cycle)}")
                cycle_assignments = self._process_cycle(cycle, state)
                assignments.extend(cycle_assignments)
                
                # Remove assigned tasks from remaining
                for task in cycle:
                    if task in remaining_tasks:
                        remaining_tasks.remove(task)
            else:
                # Step h.3: Find a chain (rule e: highest priority task)
                chain = self._find_chain(remaining_tasks, state)
                
                if chain:
                    self.logger.debug(f"Found chain of length {len(chain)}")
                    chain_assignments = self._process_chain(chain, state)
                    assignments.extend(chain_assignments)
                    
                    # Remove assigned tasks from remaining (except last one goes to waiting list)
                    for task in chain[:-1]:
                        if task in remaining_tasks:
                            remaining_tasks.remove(task)
                    # Last task in chain goes to waiting list, remove from remaining
                    if chain[-1] in remaining_tasks:
                        remaining_tasks.remove(chain[-1])
                else:
                    # No cycle and no chain - all remaining tasks go to waiting list
                    self.logger.warning("No cycles or chains found, assigning remaining tasks to waiting list")
                    for task in remaining_tasks:
                        assignments.append(TTCCAssignment(task=task, resource=None))
                        state.waiting_list_tasks.add(task)
                    break
        
        self.logger.info(f"TTCC completed: {len(assignments)} assignments made")
        return assignments
    
    def _update_preferences(
        self, 
        tasks: List[QuantumTask], 
        state: TTCCState
    ) -> None:
        """
        Update the preference pointers for each task.
        
        Each task points to its most preferred compatible resource that is:
        - Compatible with the task
        - Not already assigned to another task (or available)
        """
        for task in tasks:
            if task in state.assigned_tasks:
                continue
            
            # Get preference list for this task
            preference_list = get_task_preference_list(task, self.qnodes)
            
            # Find the first available resource in preference list
            preferred_resource = None
            for qnode in preference_list:
                # Check if resource is available (not assigned to another task)
                current_owner = state.resource_to_task.get(qnode)
                if current_owner is None or current_owner in state.assigned_tasks:
                    preferred_resource = qnode
                    break
            
            # If no compatible resource available, point to waiting list
            state.task_to_resource[task] = preferred_resource
            
            if preferred_resource:
                self.logger.debug(
                    f"Task {task.id} points to resource {preferred_resource.backend.name}"
                )
            else:
                self.logger.debug(f"Task {task.id} points to waiting list")
    
    def _find_cycle(
        self, 
        tasks: List[QuantumTask], 
        state: TTCCState
    ) -> Optional[List[QuantumTask]]:
        """
        Find a cycle in the preference graph.
        
        A cycle exists when: task1 -> resource1 -> task2 -> resource2 -> ... -> task1
        
        Returns:
            List of tasks forming a cycle, or None if no cycle exists
        """
        visited = set()
        
        for start_task in tasks:
            if start_task in visited or start_task in state.assigned_tasks:
                continue
            
            # Try to find a cycle starting from this task
            path = []
            current = start_task
            seen_in_path = set()
            
            while current is not None:
                if current in seen_in_path:
                    # Found a cycle! Extract the cycle from the path
                    # The cycle starts where we first saw current and continues to the end
                    cycle_start_idx = path.index(current)
                    cycle = path[cycle_start_idx:]
                    return cycle
                
                if current in visited:
                    break
                
                path.append(current)
                seen_in_path.add(current)
                visited.add(current)
                
                # Follow the pointer: task -> resource -> task
                preferred_resource = state.task_to_resource.get(current)
                if preferred_resource is None:
                    # Points to waiting list, no cycle
                    break
                
                # Find which task owns this resource
                resource_owner = state.resource_to_task.get(preferred_resource)
                if resource_owner is None:
                    # Resource is free, no cycle
                    break
                
                current = resource_owner
        
        return None
    
    def _process_cycle(
        self, 
        cycle: List[QuantumTask], 
        state: TTCCState
    ) -> List[TTCCAssignment]:
        """
        Process a cycle by assigning resources to all tasks in the cycle.
        
        Args:
            cycle: List of tasks forming a cycle
            state: Current TTCC state
            
        Returns:
            List of assignments made
        """
        assignments = []
        
        # In a cycle, each task gets the resource that the next task was pointing to
        # Cycle: task1 -> resource1 -> task2 -> resource2 -> ... -> task1
        for i, task in enumerate(cycle):
            next_idx = (i + 1) % len(cycle)
            next_task = cycle[next_idx]
            
            # The resource that next_task points to is assigned to current task
            resource = state.task_to_resource.get(next_task)
            
            if resource:
                assignments.append(TTCCAssignment(task=task, resource=resource))
                state.assigned_tasks.add(task)
                state.resource_to_task[resource] = task
                self.logger.debug(
                    f"Cycle assignment: Task {task.id} -> Resource {resource.backend.name}"
                )
            else:
                # Should not happen in a valid cycle, but handle gracefully
                assignments.append(TTCCAssignment(task=task, resource=None))
                state.assigned_tasks.add(task)
                state.waiting_list_tasks.add(task)
                self.logger.warning(
                    f"Cycle assignment: Task {task.id} -> Waiting list (unexpected)"
                )
        
        return assignments
    
    def _find_chain(
        self, 
        tasks: List[QuantumTask], 
        state: TTCCState
    ) -> Optional[List[QuantumTask]]:
        """
        Find a chain starting with the highest priority task (rule e).
        
        A chain is: task1 -> resource1 -> task2 -> resource2 -> ... -> taskN -> (waiting list or free resource)
        
        Rule e: Start with the highest priority task, but keep items in the system.
        
        Returns:
            List of tasks forming a chain, or None if no chain exists
        """
        if not tasks:
            return None
        
        # Sort tasks by priority (higher priority first)
        # If priorities are equal, use task ID as tiebreaker
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (t.priority, -t.id),
            reverse=True
        )
        
        # Try to find a chain starting from highest priority task
        for start_task in sorted_tasks:
            if start_task in state.assigned_tasks:
                continue
            
            chain = []
            current = start_task
            seen_in_chain = set()
            
            while current is not None:
                if current in seen_in_chain:
                    # Found a cycle, which should have been caught earlier
                    # But handle it by breaking
                    break
                
                chain.append(current)
                seen_in_chain.add(current)
                
                # Follow the pointer
                preferred_resource = state.task_to_resource.get(current)
                if preferred_resource is None:
                    # Points to waiting list - end of chain
                    break
                
                # Find which task owns this resource
                resource_owner = state.resource_to_task.get(preferred_resource)
                if resource_owner is None:
                    # Resource is free - end of chain
                    break
                
                if resource_owner in state.assigned_tasks:
                    # Resource already assigned - end of chain
                    break
                
                current = resource_owner
            
            if len(chain) > 0:
                return chain
        
        return None
    
    def _process_chain(
        self, 
        chain: List[QuantumTask], 
        state: TTCCState
    ) -> List[TTCCAssignment]:
        """
        Process a chain by assigning resources to all tasks except the last.
        The last task goes to the waiting list.
        
        Args:
            chain: List of tasks forming a chain
            state: Current TTCC state
            
        Returns:
            List of assignments made
        """
        assignments = []
        
        # In a chain, each task (except the last) gets the resource that the next task points to
        for i in range(len(chain) - 1):
            task = chain[i]
            next_task = chain[i + 1]
            
            # The resource that next_task points to is assigned to current task
            resource = state.task_to_resource.get(next_task)
            
            if resource:
                assignments.append(TTCCAssignment(task=task, resource=resource))
                state.assigned_tasks.add(task)
                state.resource_to_task[resource] = task
                self.logger.debug(
                    f"Chain assignment: Task {task.id} -> Resource {resource.backend.name}"
                )
            else:
                # Next task points to waiting list, so current task also goes to waiting list
                assignments.append(TTCCAssignment(task=task, resource=None))
                state.assigned_tasks.add(task)
                state.waiting_list_tasks.add(task)
                self.logger.debug(f"Chain assignment: Task {task.id} -> Waiting list")
        
        # Last task in chain goes to waiting list
        last_task = chain[-1]
        assignments.append(TTCCAssignment(task=last_task, resource=None))
        state.assigned_tasks.add(last_task)
        state.waiting_list_tasks.add(last_task)
        self.logger.debug(f"Chain assignment: Task {last_task.id} -> Waiting list (end of chain)")
        
        return assignments

