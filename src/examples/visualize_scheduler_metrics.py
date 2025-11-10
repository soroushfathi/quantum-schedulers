"""
Scheduler Metrics Visualization
--------------------------------
This script runs a scheduler simulation and generates comprehensive
visualization charts for analyzing scheduler performance.
"""

import simpy
from qiskit import QuantumCircuit
import random
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from pathlib import Path
import numpy as np
from typing import List, Dict

from src.Experiments.QNodeFactory import QNodeFactory
from src.qschedulers.cloud.orchestrator import Orchestrator
from src.qschedulers.cloud.task_queue import FailedTaskQueue
from src.qschedulers.cloud.qnode import QuantumNode
from src.qschedulers.cloud.qtask import QuantumTask
from src.qschedulers.schedulers.round_robin import RoundRobinScheduler
from src.qschedulers.schedulers.fan import FANScheduler
from src.logger_config import setup_logger
from src.Experiments.QTaskFactory import QTaskFactory

logger = setup_logger()

# Set style for better-looking plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)
plt.rcParams['font.size'] = 10


class MetricsCollector:
    """Collects metrics during simulation for visualization."""
    
    def __init__(self, orchestrator: Orchestrator):
        self.orchestrator = orchestrator
        self.queue_sizes = []
        self.failed_queue_sizes = []
        self.timestamps = []
        self.ttcc_failure_counts = []
        
    def collect_snapshot(self, time: float):
        """Collect a snapshot of current state."""
        self.timestamps.append(time)
        self.queue_sizes.append(self.orchestrator.task_queue.size())
        self.failed_queue_sizes.append(self.orchestrator.failed_task_queue.size())
        
        # Collect TTCC failure counts from failed queue
        failed_tasks = []
        temp_queue = []
        while not self.orchestrator.failed_task_queue.is_empty():
            task = self.orchestrator.failed_task_queue.dequeue()
            if task:
                failed_tasks.append(task)
                temp_queue.append(task)
        
        # Restore queue
        for task in temp_queue:
            self.orchestrator.failed_task_queue.enqueue(task)
        
        failure_counts = [task.ttcc_failure_count for task in failed_tasks]
        self.ttcc_failure_counts.append(failure_counts if failure_counts else [0])


def run_simulation(num_tasks: int = 100, scheduler_type: str = "FAN", 
                   enable_ttcc: bool = True, simulation_time: float = 10000) -> tuple:
    """Run the scheduler simulation and collect results."""
    logger.info(f"Starting simulation with {num_tasks} tasks, scheduler={scheduler_type}, TTCC={enable_ttcc}")
    
    # Initialize simulation environment
    env = simpy.Environment()
    
    # Create quantum nodes
    QnodeFactory = QNodeFactory(env)
    qnodes = QnodeFactory.create_cluster()
    
    # Initialize scheduler
    if scheduler_type == "FAN":
        scheduler = FANScheduler()
    else:
        scheduler = RoundRobinScheduler()
    
    failed_q = FailedTaskQueue()
    orchestrator = Orchestrator(
        env=env,
        scheduler=scheduler,
        qnodes=qnodes,
        failed_task_queue=failed_q,
        batch_size=5,
        schedule_interval=10.0,
        enable_ttcc=enable_ttcc
    )
    
    # Create metrics collector
    metrics = MetricsCollector(orchestrator)
    
    # Generate tasks
    TaskGenerator = QTaskFactory()
    tasks = []
    for i in range(num_tasks):
        tasks.append(TaskGenerator.get_a_random_task(i))
    
    logger.info(f"Created {len(tasks)} tasks")
    
    # Submit tasks
    orchestrator.submit(tasks)
    
    # Collect metrics periodically during simulation
    def collect_metrics():
        while True:
            yield env.timeout(100)  # Collect every 100 time units
            metrics.collect_snapshot(env.now)
    
    env.process(collect_metrics())
    
    # Run simulation
    env.run(until=simulation_time)
    
    # Final metrics collection
    metrics.collect_snapshot(env.now)
    
    return orchestrator, metrics, tasks


def create_visualizations(orchestrator: Orchestrator, metrics: MetricsCollector, 
                          tasks: List[QuantumTask], output_dir: Path):
    """Create comprehensive visualization charts."""
    
    results_df = pd.DataFrame(orchestrator.results)
    
    if results_df.empty:
        logger.warning("No results to visualize")
        return
    
    # Create figure with subplots
    fig = plt.figure(figsize=(20, 24))
    gs = fig.add_gridspec(6, 3, hspace=0.3, wspace=0.3)
    
    # 1. Task Status Distribution (Pie Chart)
    ax1 = fig.add_subplot(gs[0, 0])
    status_counts = results_df['status'].value_counts()
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    ax1.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%',
            colors=colors[:len(status_counts)], startangle=90)
    ax1.set_title('Task Status Distribution', fontsize=12, fontweight='bold')
    
    # 2. Success vs Failure Over Time
    ax2 = fig.add_subplot(gs[0, 1])
    if 'finish_time' in results_df.columns:
        results_df['finish_time'] = pd.to_numeric(results_df['finish_time'], errors='coerce')
        time_bins = np.linspace(0, results_df['finish_time'].max(), 20)
        results_df['time_bin'] = pd.cut(results_df['finish_time'], bins=time_bins)
        
        success_over_time = results_df[results_df['status'] == 'success'].groupby('time_bin').size()
        failed_over_time = results_df[results_df['status'] == 'failed'].groupby('time_bin').size()
        
        ax2.plot(range(len(success_over_time)), success_over_time.values, 
                marker='o', label='Success', linewidth=2, color='#2ecc71')
        ax2.plot(range(len(failed_over_time)), failed_over_time.values, 
                marker='s', label='Failed', linewidth=2, color='#e74c3c')
        ax2.set_xlabel('Time Bin')
        ax2.set_ylabel('Number of Tasks')
        ax2.set_title('Task Completion Over Time', fontsize=12, fontweight='bold')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
    
    # 3. Waiting Time Distribution
    ax3 = fig.add_subplot(gs[0, 2])
    completed_df = results_df[results_df['status'] == 'success']
    if not completed_df.empty and 'waiting_time' in completed_df.columns:
        completed_df['waiting_time'] = pd.to_numeric(completed_df['waiting_time'], errors='coerce')
        ax3.hist(completed_df['waiting_time'].dropna(), bins=30, color='#3498db', edgecolor='black', alpha=0.7)
        ax3.axvline(completed_df['waiting_time'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {completed_df["waiting_time"].mean():.2f}')
        ax3.set_xlabel('Waiting Time')
        ax3.set_ylabel('Frequency')
        ax3.set_title('Waiting Time Distribution', fontsize=12, fontweight='bold')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # 4. Turnaround Time Distribution
    ax4 = fig.add_subplot(gs[1, 0])
    if not completed_df.empty and 'turnaround_time' in completed_df.columns:
        completed_df['turnaround_time'] = pd.to_numeric(completed_df['turnaround_time'], errors='coerce')
        ax4.hist(completed_df['turnaround_time'].dropna(), bins=30, color='#9b59b6', edgecolor='black', alpha=0.7)
        ax4.axvline(completed_df['turnaround_time'].mean(), color='red', linestyle='--', 
                   linewidth=2, label=f'Mean: {completed_df["turnaround_time"].mean():.2f}')
        ax4.set_xlabel('Turnaround Time')
        ax4.set_ylabel('Frequency')
        ax4.set_title('Turnaround Time Distribution', fontsize=12, fontweight='bold')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
    
    # 5. Queue Sizes Over Time
    ax5 = fig.add_subplot(gs[1, 1])
    if metrics.timestamps:
        ax5.plot(metrics.timestamps, metrics.queue_sizes, label='Main Queue', 
                linewidth=2, color='#3498db', marker='o', markersize=3)
        ax5.plot(metrics.timestamps, metrics.failed_queue_sizes, label='Failed Queue', 
                linewidth=2, color='#e74c3c', marker='s', markersize=3)
        ax5.set_xlabel('Simulation Time')
        ax5.set_ylabel('Queue Size')
        ax5.set_title('Queue Sizes Over Time', fontsize=12, fontweight='bold')
        ax5.legend()
        ax5.grid(True, alpha=0.3)
    
    # 6. Backend Utilization
    ax6 = fig.add_subplot(gs[1, 2])
    if 'backend' in results_df.columns:
        backend_counts = results_df['backend'].value_counts()
        ax6.barh(range(len(backend_counts)), backend_counts.values, color='#16a085')
        ax6.set_yticks(range(len(backend_counts)))
        ax6.set_yticklabels(backend_counts.index)
        ax6.set_xlabel('Number of Tasks')
        ax6.set_title('Backend Utilization', fontsize=12, fontweight='bold')
        ax6.grid(True, alpha=0.3, axis='x')
    
    # 7. Fidelity Distribution
    ax7 = fig.add_subplot(gs[2, 0])
    if not completed_df.empty and 'fidelity' in completed_df.columns:
        completed_df['fidelity'] = pd.to_numeric(completed_df['fidelity'], errors='coerce')
        fidelity_data = completed_df['fidelity'].dropna()
        if not fidelity_data.empty:
            ax7.hist(fidelity_data, bins=30, color='#e67e22', edgecolor='black', alpha=0.7)
            ax7.axvline(fidelity_data.mean(), color='red', linestyle='--', 
                       linewidth=2, label=f'Mean: {fidelity_data.mean():.3f}')
            ax7.set_xlabel('Fidelity')
            ax7.set_ylabel('Frequency')
            ax7.set_title('Fidelity Distribution', fontsize=12, fontweight='bold')
            ax7.legend()
            ax7.grid(True, alpha=0.3)
    
    # 8. Execution Time vs Waiting Time
    ax8 = fig.add_subplot(gs[2, 1])
    if not completed_df.empty and 'exec_time_est' in completed_df.columns and 'waiting_time' in completed_df.columns:
        completed_df['exec_time_est'] = pd.to_numeric(completed_df['exec_time_est'], errors='coerce')
        completed_df['waiting_time'] = pd.to_numeric(completed_df['waiting_time'], errors='coerce')
        scatter_data = completed_df[['exec_time_est', 'waiting_time']].dropna()
        if not scatter_data.empty:
            ax8.scatter(scatter_data['exec_time_est'], scatter_data['waiting_time'], 
                       alpha=0.6, color='#34495e', s=50)
            ax8.set_xlabel('Execution Time')
            ax8.set_ylabel('Waiting Time')
            ax8.set_title('Execution Time vs Waiting Time', fontsize=12, fontweight='bold')
            ax8.grid(True, alpha=0.3)
    
    # 9. TTCC Failure Count Distribution
    ax9 = fig.add_subplot(gs[2, 2])
    all_failure_counts = [count for counts in metrics.ttcc_failure_counts for count in counts]
    if all_failure_counts:
        unique_counts, counts_freq = np.unique(all_failure_counts, return_counts=True)
        ax9.bar(unique_counts, counts_freq, color='#c0392b', edgecolor='black', alpha=0.7)
        ax9.set_xlabel('TTCC Failure Count')
        ax9.set_ylabel('Frequency')
        ax9.set_title('TTCC Failure Count Distribution', fontsize=12, fontweight='bold')
        ax9.set_xticks(unique_counts)
        ax9.grid(True, alpha=0.3, axis='y')
    
    # 10. Throughput Over Time
    ax10 = fig.add_subplot(gs[3, 0])
    if 'finish_time' in results_df.columns and 'status' in results_df.columns:
        results_df['finish_time'] = pd.to_numeric(results_df['finish_time'], errors='coerce')
        completed_tasks = results_df[results_df['status'] == 'success'].copy()
        if not completed_tasks.empty:
            time_windows = np.arange(0, completed_tasks['finish_time'].max() + 1000, 1000)
            throughput = []
            for i in range(len(time_windows) - 1):
                count = len(completed_tasks[
                    (completed_tasks['finish_time'] >= time_windows[i]) & 
                    (completed_tasks['finish_time'] < time_windows[i+1])
                ])
                throughput.append(count)
            
            ax10.plot(time_windows[:-1], throughput, marker='o', linewidth=2, color='#27ae60')
            ax10.set_xlabel('Simulation Time')
            ax10.set_ylabel('Tasks Completed per 1000 Time Units')
            ax10.set_title('Throughput Over Time', fontsize=12, fontweight='bold')
            ax10.grid(True, alpha=0.3)
    
    # 11. Cumulative Task Completion
    ax11 = fig.add_subplot(gs[3, 1])
    if 'finish_time' in results_df.columns:
        results_df['finish_time'] = pd.to_numeric(results_df['finish_time'], errors='coerce')
        completed_tasks = results_df[results_df['status'] == 'success'].copy()
        if not completed_tasks.empty:
            sorted_times = np.sort(completed_tasks['finish_time'].dropna())
            cumulative = np.arange(1, len(sorted_times) + 1)
            ax11.plot(sorted_times, cumulative, linewidth=2, color='#2980b9')
            ax11.set_xlabel('Simulation Time')
            ax11.set_ylabel('Cumulative Tasks Completed')
            ax11.set_title('Cumulative Task Completion', fontsize=12, fontweight='bold')
            ax11.grid(True, alpha=0.3)
    
    # 12. Swap Count Distribution (if available)
    ax12 = fig.add_subplot(gs[3, 2])
    if 'swap_count' in completed_df.columns:
        completed_df['swap_count'] = pd.to_numeric(completed_df['swap_count'], errors='coerce')
        swap_data = completed_df['swap_count'].dropna()
        if not swap_data.empty:
            ax12.hist(swap_data, bins=min(30, len(swap_data.unique())), 
                     color='#8e44ad', edgecolor='black', alpha=0.7)
            ax12.set_xlabel('Swap Count')
            ax12.set_ylabel('Frequency')
            ax12.set_title('Swap Count Distribution', fontsize=12, fontweight='bold')
            ax12.grid(True, alpha=0.3)
    
    # 13. Summary Statistics Table
    ax13 = fig.add_subplot(gs[4:, :])
    ax13.axis('off')
    
    # Calculate summary statistics
    total_tasks = len(results_df)
    completed = len(results_df[results_df['status'] == 'success'])
    failed = len(results_df[results_df['status'] == 'failed'])
    success_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0
    
    stats_data = []
    if not completed_df.empty:
        stats_data = [
            ['Metric', 'Value'],
            ['Total Tasks', f'{total_tasks}'],
            ['Completed Tasks', f'{completed}'],
            ['Failed Tasks', f'{failed}'],
            ['Success Rate', f'{success_rate:.2f}%'],
        ]
        
        if 'waiting_time' in completed_df.columns:
            completed_df['waiting_time'] = pd.to_numeric(completed_df['waiting_time'], errors='coerce')
            stats_data.extend([
                ['Avg Waiting Time', f'{completed_df["waiting_time"].mean():.2f}'],
                ['Min Waiting Time', f'{completed_df["waiting_time"].min():.2f}'],
                ['Max Waiting Time', f'{completed_df["waiting_time"].max():.2f}'],
            ])
        
        if 'turnaround_time' in completed_df.columns:
            completed_df['turnaround_time'] = pd.to_numeric(completed_df['turnaround_time'], errors='coerce')
            stats_data.extend([
                ['Avg Turnaround Time', f'{completed_df["turnaround_time"].mean():.2f}'],
                ['Min Turnaround Time', f'{completed_df["turnaround_time"].min():.2f}'],
                ['Max Turnaround Time', f'{completed_df["turnaround_time"].max():.2f}'],
            ])
        
        if 'fidelity' in completed_df.columns:
            completed_df['fidelity'] = pd.to_numeric(completed_df['fidelity'], errors='coerce')
            stats_data.extend([
                ['Avg Fidelity', f'{completed_df["fidelity"].mean():.3f}'],
                ['Min Fidelity', f'{completed_df["fidelity"].min():.3f}'],
                ['Max Fidelity', f'{completed_df["fidelity"].max():.3f}'],
            ])
        
        if 'exec_time_est' in completed_df.columns:
            completed_df['exec_time_est'] = pd.to_numeric(completed_df['exec_time_est'], errors='coerce')
            stats_data.extend([
                ['Avg Execution Time', f'{completed_df["exec_time_est"].mean():.2f}'],
            ])
    
    if stats_data:
        table = ax13.table(cellText=stats_data[1:], colLabels=stats_data[0],
                          cellLoc='left', loc='center',
                          colWidths=[0.4, 0.6])
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 2)
        ax13.set_title('Summary Statistics', fontsize=14, fontweight='bold', pad=20)
    
    # Add overall title
    fig.suptitle('Quantum Scheduler Performance Analysis', fontsize=16, fontweight='bold', y=0.995)
    
    # Save figure
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f'scheduler_metrics_{timestamp}.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    logger.info(f"Visualization saved to: {output_file}")
    
    plt.close()


def main():
    """Main function to run simulation and generate visualizations."""
    # Configuration
    num_tasks = 100
    scheduler_type = "FAN"  # or "RoundRobin"
    enable_ttcc = True
    simulation_time = 10000
    
    # Create output directory
    output_dir = Path(__file__).parent.parent.parent / 'results'
    output_dir.mkdir(exist_ok=True)
    
    # Run simulation
    orchestrator, metrics, tasks = run_simulation(
        num_tasks=num_tasks,
        scheduler_type=scheduler_type,
        enable_ttcc=enable_ttcc,
        simulation_time=simulation_time
    )
    
    # Generate visualizations
    create_visualizations(orchestrator, metrics, tasks, output_dir)
    
    # Save results to CSV
    results_df = pd.DataFrame(orchestrator.results)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = output_dir / f'quantum_scheduling_results_{timestamp}.csv'
    results_df.to_csv(results_file, index=False)
    logger.info(f"Results saved to: {results_file}")
    
    # Print summary
    logger.info("\n" + "="*50)
    logger.info("SIMULATION SUMMARY")
    logger.info("="*50)
    completed = len(results_df[results_df['status'] == 'success'])
    failed = len(results_df[results_df['status'] == 'failed'])
    logger.info(f"Total tasks: {len(tasks)}")
    logger.info(f"Completed: {completed}")
    logger.info(f"Failed: {failed}")
    logger.info(f"Success rate: {(completed/len(tasks)*100):.2f}%")
    logger.info("="*50)


if __name__ == "__main__":
    main()

