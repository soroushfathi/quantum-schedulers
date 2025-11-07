# Quantum Schedulers

**Quantum Schedulers** is a modular Python package for experimenting with **quantum task scheduling** in cloud and simulated environments.
It provides:

* � **Queue-based Task Management** — realistic simulation of task arrivals and batch processing with configurable intervals
* �📚 **Dataset utilities** for loading circuits from [MQTBench](https://github.com/cda-tum/mqt-bench) and extracting backend calibration data
* ⚡ **Pluggable schedulers** — start with a simple **Round-Robin scheduler**, and extend with greedy, RL-based, or custom algorithms
* 📊 **Evaluation tools** to estimate fidelity, execution time, and resource usage of scheduled circuits
* 📈 **Performance Analysis** — comprehensive statistics on waiting times, turnaround times, and execution metrics
* 📂 **CSV output** for easy integration into ML workflows or analysis
* ☁️ **Cloud orchestration module** — the new `cloud` module (`src/qschedulers/cloud`) provides tools for simulating and managing quantum tasks in cloud environments


---

## 📖 Running the Project with `uv`

This project uses [`uv`](https://github.com/astral-sh/uv) for fast, modern Python package management.

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/quantum-schedulers.git
cd quantum-schedulers
```

### 2. Create a virtual environment

```bash
uv venv
```

This will create a `.venv` folder inside the project.
Activate it:

* **Linux/macOS**

  ```bash
  source .venv/bin/activate
  ```
* **Windows (PowerShell)**

  ```powershell
  .venv\Scripts\Activate.ps1
  ```

### 3. Install dependencies

```bash
uv sync
```

## 🚀 Quick Start: Queue-based Scheduling

Run the queue-based scheduling example:

```bash
uv run -m src.examples.sample_queue_orchestrator
```

This example demonstrates:
- Queue-based task management with configurable batch sizes
- Periodic scheduling at fixed intervals
- Real-time task arrival simulation
- Round-robin assignment across quantum backends
- Comprehensive performance metrics including:
  - Waiting times
  - Turnaround times
  - Execution times
  - Success rates

Results are automatically saved in two CSV files:
- `quantum_scheduling_results_{timestamp}.csv`: Detailed per-task metrics
- `quantum_scheduling_stats_{timestamp}.csv`: Summary statistics

### Example Output

```
[2025-10-28 09:05:09] INFO root: Orchestrator initialized with batch processing
[2025-10-28 09:05:09] INFO root: Created 20 sample tasks
...
[2025-10-28 09:05:10] INFO root: Simulation Results:
[2025-10-28 09:05:10] INFO root: Total tasks: 20
[2025-10-28 09:05:10] INFO root: Completed tasks: 20
[2025-10-28 09:05:10] INFO root: Failed tasks: 0
[2025-10-28 09:05:10] INFO root: Average waiting time: 8.19
[2025-10-28 09:05:10] INFO root: Average turnaround time: 8.19
```

### Customizing the Simulation

Key parameters you can modify in `sample_queue_orchestrator.py`:
- `batch_size`: Number of tasks to process in each scheduling round (default: 5)
- `schedule_interval`: Time between scheduling decisions (default: 10.0)
- Number and type of quantum backends
- Task arrival time distribution

This reads the `pyproject.toml` and installs all required dependencies (Qiskit, MQTBench, pandas, etc.).

### 4. Run an example

```bash
uv run python -m src.examples.sample_cloud
```

Or open one of the example notebooks under `examples/` in Jupyter.


---


