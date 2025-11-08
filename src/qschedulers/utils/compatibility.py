"""
Compatibility Utilities
----------------------
Functions to check compatibility between quantum tasks and quantum nodes.
"""

from typing import List, Optional, Set
try:
    from qiskit import transpile
    from qiskit.circuit import QuantumCircuit
except ImportError:
    # qiskit may not be available in all environments
    pass

from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.cloud.qnode import QuantumNode
from src.logger_config import setup_logger

logger = setup_logger()


def is_task_compatible_with_resource(
    task: QuantumTask, 
    qnode: QuantumNode,
    check_transpile: bool = True
) -> bool:
    """
    Check if a task is compatible with a quantum node resource.
    
    A task is considered compatible if:
    1. The node has enough qubits for the circuit
    2. The circuit can be transpiled for the backend (gate set compatibility)
    3. The backend is available (not currently in use, if checking availability)
    
    Args:
        task: The quantum task to check
        qnode: The quantum node resource to check against
        check_transpile: If True, attempt transpilation to verify gate set compatibility
        
    Returns:
        True if compatible, False otherwise
    """
    try:
        # Check qubit requirement
        required_qubits = task.circuit.num_qubits
        available_qubits = qnode.backend.configuration().n_qubits
        
        if required_qubits > available_qubits:
            logger.debug(
                f"Task {task.id} incompatible: requires {required_qubits} qubits, "
                f"but {qnode.backend.name} has only {available_qubits}"
            )
            return False
        
        # Check gate set compatibility by attempting transpilation
        if check_transpile:
            try:
                from qiskit import transpile
                # Attempt to transpile - if it fails, the task is incompatible
                transpile(
                    task.circuit, 
                    backend=qnode.backend, 
                    optimization_level=0  # Minimal optimization for compatibility check
                )
            except ImportError:
                # qiskit not available, skip transpilation check
                logger.debug("qiskit not available, skipping transpilation check")
            except Exception as e:
                logger.debug(
                    f"Task {task.id} incompatible with {qnode.backend.name}: "
                    f"transpilation failed: {str(e)}"
                )
                return False
        
        return True
        
    except Exception as e:
        logger.warning(
            f"Error checking compatibility for task {task.id} and {qnode.backend.name}: {str(e)}"
        )
        return False


def get_compatible_resources(
    task: QuantumTask,
    qnodes: List[QuantumNode]
) -> List[QuantumNode]:
    """
    Get a list of quantum nodes that are compatible with the given task.
    
    Args:
        task: The quantum task
        qnodes: List of available quantum nodes
        
    Returns:
        List of compatible quantum nodes, ordered by preference (if applicable)
    """
    compatible = []
    for qnode in qnodes:
        if is_task_compatible_with_resource(task, qnode):
            compatible.append(qnode)
    return compatible


def get_task_preference_list(
    task: QuantumTask,
    qnodes: List[QuantumNode]
) -> List[QuantumNode]:
    """
    Get a preference-ordered list of compatible resources for a task.
    
    Currently orders by:
    1. Number of qubits (more qubits = higher preference, assuming better resources)
    2. Task priority (if applicable)
    
    Args:
        task: The quantum task
        qnodes: List of available quantum nodes
        
    Returns:
        List of compatible quantum nodes ordered by preference (most preferred first)
    """
    compatible = get_compatible_resources(task, qnodes)
    
    # Sort by number of qubits (descending) - more qubits generally means better capability
    # In a more sophisticated implementation, this could consider:
    # - Error rates
    # - Gate fidelities
    # - Estimated execution time
    # - Current queue length
    compatible.sort(
        key=lambda qn: qn.backend.configuration().n_qubits,
        reverse=True
    )
    
    return compatible

