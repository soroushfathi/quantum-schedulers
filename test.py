from mqt.bench import get_benchmark, BenchmarkLevel
from qiskit_ibm_runtime.fake_provider import FakeHanoiV2, FakeBrisbane
from qiskit_aer import backends

benchmark = get_benchmark("qft", level=BenchmarkLevel.ALG, circuit_size=5)

backend = FakeBrisbane()

print(benchmark.draw())
print(benchmark.data)