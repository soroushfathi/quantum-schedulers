from qiskit_ibm_runtime.fake_provider import (
    FakeAuckland,
    FakeHanoiV2,
    FakeKolkataV2,
    FakeBrisbane,
    FakeSherbrooke,
)
from src.qschedulers.cloud.qnode import QuantumNode
from src.logger_config import setup_logger
logger = setup_logger()

class QNodeFactory:
    """
    Factory to create a cluster of QuantumNodes with qubit counts in their names.
    """
    def __init__(self, env):
        self.env = env

    def create_cluster(self):
        backends = [
            FakeAuckland(),
            FakeHanoiV2(),
            FakeKolkataV2(),
            FakeBrisbane(),
            FakeSherbrooke()
        ]

        qnodes = []
        for backend in backends:
            n_qubits = backend.configuration().n_qubits
            name = f"{backend.name}-{n_qubits}qubits"
            node = QuantumNode(self.env, backend, name=name)
            qnodes.append(node)
            logger.info(f"'Created QuantumNode': {name} with {n_qubits} qubits")

        return qnodes
