from mqt.bench import get_benchmark, BenchmarkLevel
from src.qschedulers.cloud.qtask import QuantumTask
import random
from src.logger_config import setup_logger
logger = setup_logger()

random.seed(1234)


class QTaskFactory:
    """
    Factory class for creating quantum tasks using MQT Bench benchmarks.
    Each method corresponds to a supported benchmark algorithm.

    List of available benchmark in mqt-bench library:

     	Actual Benchmark	                                                benchmark_name
     	÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷
    0	Amplitude Estimation	                                            ae
    1	Cardinality Circuit (QUARK)	                                        bmw_quark_cardinality
    2	Copula Circuit (QUARK)	                                            bmw_quark_copula
    3	Bernstein-Vazirani	                                                bv
    4	Cuccaro-Draper-Kutin-Moulton (CDKM)                                 Ripple-Carry Adder	cdkm_ripple_carry_adder
    5	Deutsch-Jozsa	                                                    dj
    6	Draper QFT Adder	                                                draper_qft_adder
    7	Full Adder	                                                        full_adder
    8	GHZ State	                                                        ghz
    9	Graph State	                                                        graphstate
    10	Grover's Algorithm	                                                grover
    11	Half Adder	                                                        half_adder
    12	Harrow-Hassidim-Lloyd Algorithm (HHL)	                            hhl
    13	Häner-Roetteler-Svore (HRS) Cumulative Multiplier	                hrs_cumulative_multiplier
    14	Modular Adder	                                                    modular_adder
    15	Multiplier	                                                        multiplier
    16	Quantum Approximation Optimization Algorithm (QAOA)	                qaoa
    17	Quantum Fourier Transformation (QFT)	                            qft
    18	QFT with GHZ state input	                                        qftentangled
    19	Quantum Neural Network (QNN)	                                    qnn
    20	Quantum Phase Estimation (QPE) exactly representable phase	        qpeexact
    21	Quantum Phase Estimation (QPE) not exactly representable phase	    qpeinexact
    22	Quantum Walk	                                                    qwalk
    23	Random Quantum Circuit	                                            randomcircuit
    24	Ruiz-Garcia (RG) QFT Multiplier	                                    rg_qft_multiplier
    25	Shor's Algorithm	                                                shor
    26	Vedral-Barenco-Eker (VBE) Ripple-Carry Adder	                    vbe_ripple_carry_adder
    27	Real Amplitudes ansatz	                                            vqe_real_amp
    28	Efficient SU2 ansatz	                                            vqe_su2
    29	Two-local ansatz	                                                vqe_two_local
    30	W-State	                                                            wstate
    """

    def create_ae_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Amplitude Estimation (AE)
        - benchmark_name: 'ae'
        - Description:
            The Amplitude Estimation algorithm estimates the amplitude (probability weight)
            of a target quantum state. It is widely used in quantum finance, probability
            estimation, and Monte Carlo speedups.
        - Restrictions:
            n_qubits >= 3
            Preferably a power of 2 (for optimal phase estimation accuracy)
        - Benchmark Level: BenchmarkLevel.ALG
        """
        # Assign random values if not provided
        if n_qubits is None:
            n_qubits = random.choice([3, 4, 8])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("ae", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created AE task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_bmw_quark_cardinality_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Cardinality Circuit (QUARK)
        - benchmark_name: 'bmw_quark_cardinality'
        - Description:
            The QUARK Cardinality Circuit encodes the number of '1' states (set bits)
            within a quantum register. It is primarily used in probabilistic modeling,
            combinatorial optimization, and portfolio selection problems.
        - Restrictions:
            n_qubits >= 4   (minimum required for proper binary encoding)
            Even number of qubits recommended for balanced encoding
        - Benchmark Level: BenchmarkLevel.ALG
        """
        # Assign random values if not provided
        if n_qubits is None:
            n_qubits = random.choice([4, 6, 8, 10])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("bmw_quark_cardinality", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created BMW_QUARK_CARDINALITY task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task


    def create_bmw_quark_copula_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Copula Circuit (QUARK)
        - benchmark_name: 'bmw_quark_copula'
        - Description:
            The QUARK Copula Circuit encodes dependencies between multiple quantum registers,
            analogous to copula functions in classical statistics. Useful in financial modeling
            and multivariate probabilistic computations.
        - Restrictions:
            n_qubits >= 4   (minimum for representing multiple dependent registers)
            Even number recommended for balanced encoding
        - Benchmark Level: BenchmarkLevel.ALG
        """
        # Assign random values if not provided
        if n_qubits is None:
            n_qubits = random.choice([4, 6, 8])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("bmw_quark_copula", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created BMW_QUARK_COPULA task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_bv_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Bernstein-Vazirani Algorithm (BV)
        - benchmark_name: 'bv'
        - Description:
            Determines a hidden bit string by querying a black-box oracle.
            Solves the problem in a single query using quantum parallelism.
        - Restrictions:
            n_qubits >= 2  (minimum to encode oracle + target qubit)
            No restriction on even/odd
        - Benchmark Level: BenchmarkLevel.ALG
        """
        # Assign random values if not provided
        if n_qubits is None:
            n_qubits = random.choice([2, 3, 4, 5])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("bv", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created BV task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_cdkm_ripple_carry_adder_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Cuccaro-Draper-Kutin-Moulton (CDKM) Ripple-Carry Adder
        - benchmark_name: 'cdkm_ripple_carry_adder'
        - Description:
            Implements a quantum ripple-carry adder for binary addition.
            Efficient for adding two n-bit numbers using a minimal number of qubits.
        - Restrictions:
            n_qubits must be an even integer ≥ 4
            Typically n_qubits = 2 * num_bits + 1 for n-bit addition
        - Benchmark Level: BenchmarkLevel.ALG
        """
        # Assign valid random values if not provided
        if n_qubits is None:
            n_qubits = random.choice([4, 6, 8, 10, 12])  # must be even and ≥ 4
        else:
            if n_qubits < 4 or n_qubits % 2 != 0:
                raise ValueError("n_qubits must be an even integer ≥ 4 for CDKM Ripple-Carry Adder.")

        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("cdkm_ripple_carry_adder", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created CDKM Ripple-Carry Adder task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_deutsch_jozsa_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Deutsch-Jozsa (DJ) Algorithm
        - benchmark_name: 'dj'
        - Description:
            Implements the Deutsch-Jozsa algorithm to determine whether a given
            boolean function is constant or balanced. This is one of the first
            examples showing exponential speedup of a quantum algorithm.
        - Restrictions:
            n_qubits >= 2 (minimum for oracle + input register)
            Typical sizes: 2–10 qubits
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random values if not provided
        if n_qubits is None:
            n_qubits = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("dj", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created Deutsch-Jozsa task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_draper_qft_adder_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Draper Quantum Fourier Transform (QFT) Adder
        - benchmark_name: 'draper_qft_adder'
        - Description:
            Implements the Draper QFT adder for quantum addition using
            the Quantum Fourier Transform. Operates in the phase domain
            to add two numbers efficiently on quantum registers.
        - Restrictions:
            n_qubits >= 3  (minimum for representing two addends and the result)
            Typical: n_qubits = 2 * num_bits (for adding two n-bit numbers)
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random values if not provided
        if n_qubits is None:
            # Use even numbers to simulate realistic register pairs
            n_qubits = random.choice([4, 6, 8, 10, 12])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("draper_qft_adder", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created Draper QFT Adder task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_full_adder_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Full Adder Circuit (Quantum)
        - benchmark_name: 'full_adder'
        - Description:
            Implements a quantum version of the classical full adder.
            Adds two binary digits and a carry input, producing sum and carry output.
        - Restrictions:
            n_qubits must be an even integer ≥ 4 (per MQT Bench)
            Typical sizes: 4, 6, 8, 10
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # --- Step 1: Assign valid number of qubits ---
        if n_qubits is None:
            n_qubits = random.choice([4, 6, 8, 10])
        else:
            if n_qubits < 4:
                logger.warning(f"n_qubits={n_qubits} too small; adjusted to 4.")
                n_qubits = 4
            elif n_qubits % 2 != 0:
                adjusted_n = n_qubits + 1
                logger.warning(
                    f"n_qubits={n_qubits} is odd; adjusted to nearest even value {adjusted_n}."
                )
                n_qubits = adjusted_n

        # --- Step 2: Random arrival time if not provided ---
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # --- Step 3: Create benchmark circuit ---
        circuit = get_benchmark("full_adder", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # --- Step 4: Log task creation ---
        logger.info(
            f"[QTaskFactory] Created Full Adder task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_ghz_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        GHZ State (Greenberger–Horne–Zeilinger)
        - benchmark_name: 'ghz'
        - Description:
            Prepares an entangled GHZ state of the form (|000...0⟩ + |111...1⟩) / √2.
            This state is a key resource in quantum communication and error correction.
        - Restrictions:
            n_qubits >= 2 (minimum for entanglement)
            Typically 3–10 qubits for demonstration and benchmarking.
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined parameters
        if n_qubits is None:
            n_qubits = random.choice([3, 4, 5, 6, 7, 8, 9, 10])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("ghz", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created GHZ task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_graphstate_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Graph State
        - benchmark_name: 'graphstate'
        - Description:
            Generates a multi-qubit entangled graph state, where vertices represent qubits
            and edges represent controlled-Z entanglement between them.
            These states are widely used in measurement-based quantum computing (MBQC)
            and quantum network simulations.
        - Restrictions:
            n_qubits >= 2 (minimum for a connected graph)
            Typically 3–12 qubits for benchmarking and scalability tests.
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined parameters
        if n_qubits is None:
            n_qubits = random.choice([3, 4, 5, 6, 7, 8, 9, 10, 11, 12])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("graphstate", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created GraphState task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_grover_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Grover's Algorithm
        - benchmark_name: 'grover'
        - Description:
            Implements Grover's search algorithm for unstructured database search.
            Provides a quadratic speedup over classical search methods.
            Typically demonstrates amplitude amplification using an oracle and diffuser.
        - Restrictions:
            n_qubits >= 3 (minimum meaningful problem size)
            Typically 3–10 qubits for simulation and benchmarking.
            No parity constraint (even/odd both fine).
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined parameters
        if n_qubits is None:
            n_qubits = random.choice([3, 4, 5, 6, 7, 8, 9, 10])
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("grover", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created Grover task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_half_adder_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Half Adder Circuit (Quantum)
        - benchmark_name: 'half_adder'
        - Description:
            Implements the quantum version of a classical Half Adder.
            Adds two 1-bit numbers (A and B) to produce a sum and carry output.
            Used as a minimal example of quantum arithmetic circuits.
        - Restrictions:
            n_qubits must be an odd integer ≥ 3
            Typically 3, 5, 7, or 9 are used.
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined parameters
        if n_qubits is None:
            n_qubits = random.choice([3, 5, 7, 9])  # only odd numbers ≥3
        else:
            # Ensure n_qubits satisfies restriction
            if n_qubits < 3 or n_qubits % 2 == 0:
                raise ValueError("n_qubits must be an odd integer ≥ 3 for Half Adder benchmark")

        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("half_adder", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created Half Adder task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_hhl_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Harrow–Hassidim–Lloyd Algorithm (HHL)
        - benchmark_name: 'hhl'
        - Description:
            Implements the HHL algorithm, a quantum algorithm for solving systems
            of linear equations of the form A·x = b.
            It demonstrates an exponential speedup in certain conditions compared
            to classical solvers and serves as a benchmark for quantum linear algebra.
        - Restrictions:
            n_qubits must be even and ≥ 4
            (due to the need for ancilla qubits and encoding of matrix & vector)
            Typical sizes: 4, 6, 8, 10
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined parameters
        if n_qubits is None:
            n_qubits = random.choice([4, 6, 8, 10])  # even numbers only
        else:
            if n_qubits < 4 or n_qubits % 2 != 0:
                raise ValueError("n_qubits must be an even integer ≥ 4 for HHL benchmark")

        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("hhl", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created HHL task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_hrs_cumulative_multiplier_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Häner–Roetteler–Svore (HRS) Cumulative Multiplier
        - benchmark_name: 'hrs_cumulative_multiplier'
        - Description:
            Implements the Häner–Roetteler–Svore cumulative multiplier circuit,
            which performs modular multiplication in a quantum register.
            Used as a key subroutine in quantum arithmetic and Shor's factoring algorithm.
        - Restrictions (from MQT Bench):
            n_qubits must be an integer ≥ 5 and (n_qubits - 1) must be divisible by 4.
            Valid sizes: 5, 9, 13, 17, 21, ...
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # --- Step 1: Assign valid number of qubits ---
        if n_qubits is None:
            n_qubits = random.choice([5, 9, 13, 17, 21])  # valid quantum register sizes
        else:
            # Validation and auto-correction
            if n_qubits < 5:
                logger.warning(f"n_qubits={n_qubits} too small; adjusted to 5.")
                n_qubits = 5
            elif (n_qubits - 1) % 4 != 0:
                adjusted_n = ((n_qubits - 1) // 4 + 1) * 4 + 1
                logger.warning(
                    f"n_qubits={n_qubits} invalid; adjusted to nearest valid value {adjusted_n}."
                )
                n_qubits = adjusted_n

        # --- Step 2: Random arrival time if not provided ---
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # --- Step 3: Create benchmark circuit ---
        circuit = get_benchmark("hrs_cumulative_multiplier", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # --- Step 4: Log task creation ---
        logger.info(
            f"[QTaskFactory] Created HRS Cumulative Multiplier task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_modular_adder_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Modular Adder Circuit (Quantum)
        - benchmark_name: 'modular_adder'
        - Description:
            Implements a quantum modular adder, performing addition modulo N.
            Useful in quantum arithmetic and subroutines for Shor's algorithm.
        - Restrictions:
            n_qubits must be an even integer ≥ 4
            Typical sizes: 4, 6, 8, 10, 12
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Step 1: Ensure valid n_qubits
        if n_qubits is None:
            n_qubits = random.choice([4, 6, 8, 10, 12])
        else:
            if n_qubits < 4:
                logger.warning(f"n_qubits={n_qubits} too small; adjusted to 4.")
                n_qubits = 4
            elif n_qubits % 2 != 0:
                adjusted_n = n_qubits + 1
                logger.warning(
                    f"n_qubits={n_qubits} is odd; adjusted to nearest even value {adjusted_n}."
                )
                n_qubits = adjusted_n

        # Step 2: Arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Step 3: Create circuit
        circuit = get_benchmark("modular_adder", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Step 4: Log creation
        logger.info(
            f"[QTaskFactory] Created Modular Adder task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_multiplier_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Multiplier Circuit
        - benchmark_name: 'multiplier'
        - Description:
            Implements a quantum multiplier circuit.
            Typically used in arithmetic operations in larger quantum algorithms.
        - Restrictions:
            n_qubits >= 4 and divisible by 4
            Typical sizes: 4, 8, 12, 16
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        valid_sizes = [4, 8, 12, 16, 20]
        if n_qubits is None:
            n_qubits = random.choice(valid_sizes)
        else:
            if n_qubits < 4 or n_qubits % 4 != 0:
                raise ValueError("n_qubits must be ≥ 4 and divisible by 4 for Multiplier benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit
        circuit = get_benchmark("multiplier", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created Multiplier task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_qaoa_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Quantum Approximation Optimization Algorithm (QAOA)
        - benchmark_name: 'qaoa'
        - Description:
            Implements the QAOA circuit for combinatorial optimization problems.
            Typically used for MaxCut, portfolio optimization, etc.
        - Restrictions:
            n_qubits >= 1
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice([2, 3, 4, 5, 6, 7, 8])
        else:
            if n_qubits < 1:
                raise ValueError("n_qubits must be ≥ 1 for QAOA benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit
        circuit = get_benchmark("qaoa", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created QAOA task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_qft_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Quantum Fourier Transformation (QFT)
        - benchmark_name: 'qft'
        - Description:
            Implements the Quantum Fourier Transform circuit on n_qubits.
            Used in phase estimation, Shor's algorithm, and quantum signal processing.
        - Restrictions:
            n_qubits >= 2
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice([2, 3, 4, 5, 6, 7, 8])
        else:
            if n_qubits < 2:
                raise ValueError("n_qubits must be ≥ 2 for QFT benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created QFT task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_qftentangled_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Quantum Fourier Transform (QFT) with GHZ state input
        - benchmark_name: 'qftentangled'
        - Description:
            Prepares a GHZ state as input and applies the Quantum Fourier Transform.
            Used in entanglement-based algorithms and benchmarking.
        - Restrictions:
            n_qubits >= 3 (minimum to create a GHZ state)
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice([3, 4, 5, 6, 7, 8])
        else:
            if n_qubits < 3:
                raise ValueError("n_qubits must be ≥ 3 for QFT with GHZ input benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("qftentangled", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created QFT with GHZ input task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_qnn_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Quantum Neural Network (QNN)
        - benchmark_name: 'qnn'
        - Description:
            Creates a parameterized quantum circuit for a variational quantum neural network.
            Used for machine learning tasks and benchmarking variational circuits.
        - Restrictions:
            n_qubits >= 2 (minimum for meaningful parameterized circuit)
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice([2, 3, 4, 5, 6])
        else:
            if n_qubits < 2:
                raise ValueError("n_qubits must be ≥ 2 for QNN benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("qnn", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created QNN task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_qpeinexact_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Quantum Phase Estimation (QPE) – not exactly representable phase
        - benchmark_name: 'qpeinexact'
        - Description:
            Implements the QPE algorithm for estimating eigenphases of a unitary
            operator where the phase is not exactly representable with n qubits.
            Demonstrates approximation errors and is useful for benchmarking.
        - Restrictions:
            n_qubits >= 2 (minimum meaningful estimation precision)
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice([2, 3, 4, 5, 6, 7, 8])
        else:
            if n_qubits < 2:
                raise ValueError("n_qubits must be ≥ 2 for QPE Inexact benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("qpeinexact", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created QPE Inexact task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_qwalk_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Quantum Walk
        - benchmark_name: 'qwalk'
        - Description:
            Implements a discrete-time or continuous-time quantum walk on a graph.
            Useful for exploring quantum algorithms for search, transport, and
            graph analysis.
        - Restrictions:
            n_qubits >= 2 (minimum for meaningful walk)
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice([2, 3, 4, 5, 6, 7, 8])
        else:
            if n_qubits < 2:
                raise ValueError("n_qubits must be ≥ 2 for Quantum Walk benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("qwalk", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created Quantum Walk task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    # def create_randomcircuit_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
    #     """
    #     Random Quantum Circuit
    #     - benchmark_name: 'randomcircuit'
    #     - Description:
    #         Generates a random quantum circuit with a specified number of qubits
    #         and gates. Useful for benchmarking, testing, and stress-testing
    #         quantum schedulers.
    #     - Restrictions:
    #         n_qubits >= 2
    #     - Benchmark Level: BenchmarkLevel.ALG
    #     """
    #
    #     # Assign random or user-defined n_qubits
    #     if n_qubits is None:
    #         n_qubits = random.choice([2, 3, 4, 5, 6, 7, 8, 9, 10])
    #     else:
    #         if n_qubits < 2:
    #             raise ValueError("n_qubits must be ≥ 2 for Random Quantum Circuit benchmark")
    #
    #     # Assign arrival time
    #     if arrival_time is None:
    #         arrival_time = round(random.uniform(0, 50), 2)
    #
    #     # Create circuit using MQT Bench
    #     circuit = get_benchmark("randomcircuit", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
    #     task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)
    #
    #     # Log creation
    #     logger.info(
    #         f"[QTaskFactory] Created Random Quantum Circuit task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
    #     )
    #
    #     return task

    def create_rg_qft_multiplier_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Ruiz-Garcia (RG) QFT Multiplier
        - benchmark_name: 'rg_qft_multiplier'
        - Description:
            Implements the Ruiz-Garcia QFT-based multiplier circuit.
            Used for modular multiplication leveraging Quantum Fourier Transform.
        - Restrictions:
            n_qubits must satisfy the benchmark-specific constraints
            (usually ≥ 4 and divisible by 4)
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice([4, 8, 12, 16])  # ensure divisibility by 4
        else:
            if n_qubits < 4 or n_qubits % 4 != 0:
                raise ValueError("n_qubits must be ≥ 4 and divisible by 4 for RG QFT Multiplier")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("rg_qft_multiplier", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created RG QFT Multiplier task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_shor_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Shor's Algorithm
        - benchmark_name: 'shor'
        - Description:
            Implements Shor's factoring algorithm using quantum modular exponentiation
            and Quantum Fourier Transform.
        - Restrictions:
            Only certain circuit sizes are supported by MQT Bench: 18, 42, 58, 74
        - Benchmark Level: BenchmarkLevel.ALG
        """

        VALID_SIZES = [18, 42, 58, 74]

        # Assign random or user-defined n_qubits
        if n_qubits is None:
            n_qubits = random.choice(VALID_SIZES)
        else:
            if n_qubits not in VALID_SIZES:
                raise ValueError(f"n_qubits must be one of {VALID_SIZES} for Shor's Algorithm benchmark")

        # Assign arrival time
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Create circuit using MQT Bench
        circuit = get_benchmark("shor", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log creation
        logger.info(
            f"[QTaskFactory] Created Shor's Algorithm task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_vbe_ripple_carry_adder_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        Vedral–Barenco–Eker (VBE) Ripple-Carry Adder
        - benchmark_name: 'vbe_ripple_carry_adder'
        - Description:
            Quantum ripple-carry adder for binary addition (Vedral-Barenco-Eker).
            Used as a basic arithmetic primitive in quantum computing.
        - Restrictions:
            num_qubits >= 4 and (num_qubits - 1) must be divisible by 3.
            Valid sizes: 4, 7, 10, 13, 16, 19, 22, ...
        - Benchmark Level: BenchmarkLevel.ALG
        """

        VALID_SIZES = [4, 7, 10, 13, 16, 19, 22]

        # Validate or choose n_qubits
        if n_qubits is None:
            n_qubits = random.choice(VALID_SIZES)
        else:
            if n_qubits not in VALID_SIZES:
                raise ValueError(f"n_qubits must be one of {VALID_SIZES} for VBE Ripple-Carry Adder benchmark")

        # Arrival time assignment
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Generate circuit
        circuit = get_benchmark("vbe_ripple_carry_adder", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log info
        logger.info(
            f"[QTaskFactory] Created VBE Ripple-Carry Adder task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_vqe_real_amp_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        VQE with Real Amplitudes Ansatz
        - benchmark_name: 'vqe_real_amp'
        - Description:
            Implements a parameterized quantum circuit with real amplitudes
            as the ansatz for the Variational Quantum Eigensolver (VQE).
        - Restrictions:
            n_qubits >= 1
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign n_qubits if not provided
        if n_qubits is None:
            n_qubits = random.randint(1, 8)  # choose a reasonable small size
        else:
            if n_qubits < 1:
                raise ValueError("n_qubits must be an integer >= 1 for VQE Real Amplitudes Ansatz")

        # Assign arrival time if not provided
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Generate circuit
        circuit = get_benchmark("vqe_real_amp", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created VQE Real Amplitudes task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_vqe_su2_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        VQE with Efficient SU2 Ansatz
        - benchmark_name: 'vqe_su2'
        - Description:
            Implements a parameterized quantum circuit using the Efficient SU2 ansatz
            for the Variational Quantum Eigensolver (VQE).
        - Restrictions:
            n_qubits >= 1
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign n_qubits if not provided
        if n_qubits is None:
            n_qubits = random.randint(1, 8)  # reasonable small size
        else:
            if n_qubits < 1:
                raise ValueError("n_qubits must be an integer >= 1 for VQE SU2 Ansatz")

        # Assign arrival time if not provided
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Generate circuit
        circuit = get_benchmark("vqe_su2", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created VQE SU2 task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_vqe_two_local_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        VQE with Two-Local Ansatz
        - benchmark_name: 'vqe_two_local'
        - Description:
            Implements a parameterized quantum circuit using the Two-Local ansatz
            for the Variational Quantum Eigensolver (VQE).
        - Restrictions:
            n_qubits >= 1
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign n_qubits if not provided
        if n_qubits is None:
            n_qubits = random.randint(1, 8)  # reasonable small size
        else:
            if n_qubits < 1:
                raise ValueError("n_qubits must be an integer >= 1 for VQE Two-Local Ansatz")

        # Assign arrival time if not provided
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Generate circuit
        circuit = get_benchmark("vqe_two_local", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created VQE Two-Local task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def create_wstate_task(self, task_id: int, arrival_time: float = None, n_qubits: int = None):
        """
        W-State Circuit
        - benchmark_name: 'wstate'
        - Description:
            Prepares a W-state on n_qubits. W-state is an entangled quantum state
            with exactly one qubit in |1> and the rest in |0>, symmetrically distributed.
        - Restrictions:
            n_qubits >= 2
        - Benchmark Level: BenchmarkLevel.ALG
        """

        # Assign n_qubits if not provided
        if n_qubits is None:
            n_qubits = random.randint(2, 8)  # reasonable small size
        else:
            if n_qubits < 2:
                raise ValueError("n_qubits must be an integer >= 2 for W-State benchmark")

        # Assign arrival time if not provided
        if arrival_time is None:
            arrival_time = round(random.uniform(0, 50), 2)

        # Generate circuit
        circuit = get_benchmark("wstate", level=BenchmarkLevel.ALG, circuit_size=n_qubits)
        task = QuantumTask(id=task_id, circuit=circuit, arrival_time=arrival_time)

        # Log task creation
        logger.info(
            f"[QTaskFactory] Created W-State task | id={task_id} | qubits={n_qubits} | arrival_time={arrival_time}"
        )

        return task

    def get_a_random_task(self, task_id):
        """
        Select a random benchmark task and create a QuantumTask.
        """
        task_methods = [
            self.create_ae_task,
            self.create_bmw_quark_cardinality_task,
            self.create_bmw_quark_copula_task,
            self.create_bv_task,
            self.create_cdkm_ripple_carry_adder_task,
            self.create_deutsch_jozsa_task,
            self.create_draper_qft_adder_task,
            self.create_full_adder_task,
            self.create_ghz_task,
            self.create_graphstate_task,
            self.create_grover_task,
            self.create_half_adder_task,
            self.create_hhl_task,
            self.create_hrs_cumulative_multiplier_task,
            self.create_modular_adder_task,
            self.create_multiplier_task,
            self.create_qaoa_task,
            self.create_qft_task,
            self.create_qftentangled_task,
            self.create_qnn_task,
            self.create_qpeinexact_task,
            self.create_qwalk_task,
            self.create_rg_qft_multiplier_task,
            self.create_shor_task
        ]

        chosen_method = random.choice(task_methods)

        return chosen_method(task_id)