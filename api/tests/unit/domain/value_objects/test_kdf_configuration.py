import pytest
from babylon.domain.exceptions import KdfConfigurationValidationError
from babylon.domain.value_objects import KdfConfiguration


class TestKdfConfiguration:
    @pytest.mark.parametrize(
        ("algorithm", "memory_kb", "iterations", "parallelism"),
        [
            ("argon2id", 65536, 3, 4),  # Standard OWASP recommended minimums
            ("argon2id", 131072, 4, 8),
        ],
    )
    def test_create_valid_configuration(
        self, algorithm: str, memory_kb: int, iterations: int, parallelism: int
    ) -> None:
        kdf = KdfConfiguration(
            algorithm=algorithm,
            memory_kb=memory_kb,
            iterations=iterations,
            parallelism=parallelism,
        )

        assert kdf.algorithm == algorithm
        assert kdf.memory_kb == memory_kb
        assert kdf.iterations == iterations
        assert kdf.parallelism == parallelism

    @pytest.mark.parametrize(
        ("algorithm", "memory_kb", "iterations", "parallelism"),
        [
            ("", 65536, 3, 4),  # Missing algorithm
            ("md5", 65536, 3, 4),  # Insecure/Unsupported algorithm
            ("argon2id", -1, 3, 4),  # Invalid memory
        ],
    )
    def test_cannot_create_invalid_configuration(
        self, algorithm: str, memory_kb: int, iterations: int, parallelism: int
    ) -> None:
        with pytest.raises(KdfConfigurationValidationError):
            KdfConfiguration(
                algorithm=algorithm,
                memory_kb=memory_kb,
                iterations=iterations,
                parallelism=parallelism,
            )

    @pytest.mark.parametrize(
        ("algorithm", "memory_kb", "iterations", "parallelism"),
        [
            ("argon2id", 8192, 1, 4),  # Memory and iterations too low (Unsafe)
            ("argon2id", 65536, 1, 4),  # Iterations too low
            ("argon2id", 10485760, 3, 4),  # Memory too high
            ("argon2id", 65536, 2000, 4),
            ("argon2id", 65536, 3, 0),
            ("argon2id", 65536, 3, 100),  # Iterations too high
        ],
    )
    def test_cannot_create_unsafe_configuration(
        self, algorithm: str, memory_kb: int, iterations: int, parallelism: int
    ) -> None:
        with pytest.raises(KdfConfigurationValidationError):
            KdfConfiguration(algorithm, memory_kb, iterations, parallelism)
