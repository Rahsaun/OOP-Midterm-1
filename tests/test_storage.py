"""Unit tests; no PostgreSQL server required for the JSON tests."""
import tempfile
import unittest
from pathlib import Path

from simulation import ArmedHuman, SimulationController, SimulationPlayground
from storage import JSONStorage, StateStorage


class FakeStorage(StateStorage):
    """Test double proving the controller only uses the abstract interface."""

    def __init__(self):
        self.state = None

    def save_state(self, state: dict) -> None:
        from copy import deepcopy
        self.state = deepcopy(state)

    def load_state(self) -> dict | None:
        from copy import deepcopy
        return deepcopy(self.state)


class StorageTests(unittest.TestCase):
    def test_same_controller_with_two_backends(self):
        with tempfile.TemporaryDirectory() as directory:
            for storage in (FakeStorage(), JSONStorage(Path(directory) / "state.json")):
                with self.subTest(storage=type(storage).__name__):
                    game = SimulationPlayground(150, 200)
                    game.populate(regular=5, armed=2, zombies=3)
                    game.step()
                    expected = game.to_state()
                    controller = SimulationController(storage, game)
                    controller.save()
                    restored = SimulationController(storage)
                    self.assertTrue(restored.load())
                    self.assertEqual(restored.simulation.to_state(), expected)
                    self.assertEqual(restored.simulation.tick_count, 1)
                    self.assertTrue(
                        any(isinstance(h, ArmedHuman) for h in restored.simulation.humans)
                    )

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            controller = SimulationController(JSONStorage(Path(directory) / "missing.json"))
            self.assertFalse(controller.load())


if __name__ == "__main__":
    unittest.main()
