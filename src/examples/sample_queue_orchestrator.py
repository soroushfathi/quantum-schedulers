"""
Example demonstrating the queue-based orchestrator with batch processing.
Results are saved to a CSV file for analysis.
"""

import simpy
from qiskit import QuantumCircuit
import random
import pandas as pd
from datetime import datetime
from pathlib import Path

from src.Experiments.QNodeFactory import QNodeFactory
from src.qschedulers.cloud.orchestrator import Orchestrator
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.schedulers.round_robin import RoundRobinScheduler
from src.qschedulers.schedulers.fan import FANScheduler
from src.logger_config import setup_logger
from qiskit_ibm_runtime.fake_provider import FakeHanoiV2, FakeBrisbane
from src.qschedulers.datasets.mqtbench_loader import load_mqtbench_circuits, PRESET_SMALL

logger = setup_logger()

def create_sample_circuit(num_qubits: int = 3) -> QuantumCircuit:
    """Create a sample quantum circuit for testing."""
    qc = QuantumCircuit(num_qubits)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()
    return qc

def main():
    # Initialize simulation environment
    env = simpy.Environment()
    
    # Create quantum nodes (backends)
    # qnodes = [
    #     QuantumNode(env, FakeHanoiV2(), name="Hanoi"),
    #     QuantumNode(env, FakeBrisbane(), name="Brisbane"),
    # ]

    QnodeFactory = QNodeFactory(env)
    qnodes = QnodeFactory.create_cluster()

    # Initialize scheduler and orchestrator
    # scheduler = RoundRobinScheduler()
    scheduler = FANScheduler()
    orchestrator = Orchestrator(
        env=env,
        scheduler=scheduler,
        qnodes=qnodes,
        batch_size=len(qnodes),  # Process 5 tasks at a time
        schedule_interval=2.0  # Schedule every 10 seconds
    )


    '''
    I skip it...
    
    # Load circuits from MQTBench (fallback to synthetic if loader unavailable)
    try:
        circuits = load_mqtbench_circuits(PRESET_SMALL)
        if not circuits:
            logger.warning("No circuits returned from MQTBench loader; falling back to synthetic circuits")
            circuits = [create_sample_circuit() for _ in range(3)]
        else:
            logger.info(f"Loaded {len(circuits)} circuits from MQTBench presets")
    except Exception as e:
        logger.warning(f"Failed to load MQTBench circuits: {e}; using synthetic circuits")
        circuits = [create_sample_circuit() for _ in range(3)]
        

    # Create tasks from the loaded circuits. We repeat circuits if needed to reach desired task count.
    task_count = 20
    tasks = []
    for i in range(task_count):
        base_circ = circuits[i % len(circuits)]
        # Try to copy the circuit to avoid mutating the same object
        try:
            circuit = base_circ.copy()
        except Exception:
            # fallback if copy is not available
            circuit = base_circ

        # Tasks arrive randomly between 0 and 50 time units
        arrival_time = random.uniform(0, 50)
        task = QuantumTask(i, circuit, arrival_time)
        tasks.append(task)
    '''

    # task_count = 20
    # random.seed(1234)
    #
    # tasks = []
    # for i in range(task_count):
    #     circuit = create_sample_circuit()
    #
    #     arrival_time = random.uniform(0, 50)
    #     task = QuantumTask(i, circuit, arrival_time)
    #     tasks.append(task)

    from src.Experiments.QTaskFactory import QTaskFactory
    TaskGenerator = QTaskFactory()
    tasks = []
    n_task = 100
    for i in range(n_task):
        tasks.append(TaskGenerator.get_a_random_task(i))

    
    logger.info(f"Created {len(tasks)} sample tasks")
    
    # Submit tasks to the orchestrator
    orchestrator.submit(tasks)
    
    # Run the simulation for 100 time units
    env.run(until=10000)
    
    # Convert results to DataFrame for analysis
    results_df = pd.DataFrame(orchestrator.results)
    
    # Calculate and log summary statistics
    logger.info("\nSimulation Results:")
    completed = len(results_df[results_df['status'] == 'success'])
    failed = len(results_df[results_df['status'] == 'failed'])
    logger.info(f"Total tasks: {len(tasks)}")
    logger.info(f"Completed tasks: {completed}")
    logger.info(f"Failed tasks: {failed}")
    
    # Calculate statistics for completed tasks
    completed_df = results_df[results_df['status'] == 'success']
    if not completed_df.empty:
        avg_waiting = completed_df['waiting_time'].mean()
        avg_turnaround = completed_df['turnaround_time'].mean()
        logger.info(f"Average waiting time: {avg_waiting:.2f}")
        logger.info(f"Average turnaround time: {avg_turnaround:.2f}")
        
        # Add more statistics
        stats_df = pd.DataFrame({
            'Metric': [
                'Min Waiting Time',
                'Max Waiting Time',
                'Avg Waiting Time',
                'Min Turnaround Time',
                'Max Turnaround Time',
                'Avg Turnaround Time',
                'Min Execution Time',
                'Max Execution Time',
                'Avg Execution Time',
                'Min fidelity',
                'Max fidelity',
                'Avg fidelity',
                'Success Rate (%)'
            ],
            'Value': [
                completed_df['waiting_time'].min(),
                completed_df['waiting_time'].max(),
                avg_waiting,
                completed_df['turnaround_time'].min(),
                completed_df['turnaround_time'].max(),
                avg_turnaround,
                completed_df['exec_time_est'].min(),
                completed_df['exec_time_est'].max(),
                completed_df['exec_time_est'].mean(),
                completed_df['fidelity'].min(),
                completed_df['fidelity'].max(),
                completed_df['fidelity'].mean(),
                (completed / len(tasks)) * 100
            ]
        })


        # Create results directory if it doesn't exist
        results_dir = Path(__file__).parent.parent.parent / 'results'
        results_dir.mkdir(exist_ok=True)

        # Generate timestamp for unique filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save detailed results
        results_file = results_dir / f'quantum_scheduling_results_{timestamp}.csv'
        results_df.to_csv(results_file, index=False)
        logger.info(f"\nDetailed results saved to: {results_file}")

        # Save summary statistics
        stats_file = results_dir / f'quantum_scheduling_stats_{timestamp}.csv'
        stats_df.to_csv(stats_file, index=False)
        logger.info(f"Summary statistics saved to: {stats_file}")

if __name__ == "__main__":
    main()