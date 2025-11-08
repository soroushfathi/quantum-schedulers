# TTCC Algorithm Implementation for Quantum Task Scheduler

## Overview

This document describes the implementation of the Top Trading Cycles and Chains (TTCC) algorithm for handling failed tasks in the quantum task scheduler.

## Architecture

### Components

1. **Compatibility Module** (`src/qschedulers/utils/compatibility.py`)
   - `is_task_compatible_with_resource()`: Checks if a task is compatible with a quantum node
   - `get_compatible_resources()`: Returns list of compatible resources for a task
   - `get_task_preference_list()`: Returns preference-ordered list of compatible resources

2. **TTCC Algorithm** (`src/qschedulers/utils/ttcc.py`)
   - `TTCCAlgorithm`: Main algorithm class implementing TTCC
   - `TTCCAssignment`: Data class representing task-resource assignments
   - `TTCCState`: Internal state tracking for the algorithm

3. **Failed Task Exchange Manager** (`src/qschedulers/cloud/failed_task_exchange_manager.py`)
   - `FailedTaskExchangeManager`: Manages TTCC processing for failed tasks
   - Integrates with the orchestrator to resubmit tasks

4. **Orchestrator Integration** (`src/qschedulers/cloud/orchestrator.py`)
   - Modified to use `FailedTaskExchangeManager` when tasks fail
   - Automatically triggers TTCC processing on task failures

## Algorithm Flow

### Step h.1: Preference Update
Each failed task points to its most preferred compatible resource. If no resource is acceptable, the task points to the "waiting list".

### Step h.2: Cycle Detection
If a cycle is found in the graph (task1 → resource1 → task2 → resource2 → ... → task1), all tasks in the cycle are assigned to their preferred resources and removed from the queue.

### Step h.3: Chain Selection (Rule e)
If no cycle exists, a chain is selected starting with the highest priority task. All tasks in the chain (except the last) are assigned, and the last task goes to the waiting list.

### Iteration
The algorithm continues until the failed task queue is empty.

## Compatibility Criteria

A task is considered compatible with a resource if:
1. The node has sufficient qubits for the circuit
2. The circuit can be transpiled for the backend (gate set compatibility)
3. The backend satisfies any availability constraints

## Integration Points

### Orchestrator
- When a task fails, it is added to the `FailedTaskQueue`
- The orchestrator triggers TTCC processing via `FailedTaskExchangeManager`
- Tasks assigned by TTCC are resubmitted to the main task queue

### Resubmission
- Tasks assigned to resources are resubmitted via the callback mechanism
- Tasks assigned to the waiting list remain in the failed queue for later retry

## Testing

Unit tests are provided in `tests/test_ttcc.py` covering:
- Cycle detection
- Chain selection
- Full algorithm execution
- Compatibility checking

## Usage

The TTCC algorithm is enabled by default in the orchestrator. To disable it:

```python
orchestrator = Orchestrator(
    env=env,
    scheduler=scheduler,
    qnodes=qnodes,
    enable_ttcc=False  # Disable TTCC
)
```

## Notes

- The algorithm uses rule e for chain selection (highest priority task first)
- Tasks maintain their priority when resubmitted
- The algorithm is non-blocking and runs asynchronously in the SimPy environment

