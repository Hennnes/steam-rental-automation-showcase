import threading
import unittest
from datetime import datetime, timedelta, timezone

from rental_core import Account, NoAccountAvailable, RentalManager


class RentalManagerTests(unittest.TestCase):
    def test_account_is_reserved_and_returned(self):
        manager = RentalManager([Account("A-1", "Game")])

        rental = manager.issue_rental(
            order_id="O-1",
            game="Game",
            duration_hours=1,
        )

        self.assertEqual(manager.available_accounts("Game"), [])
        manager.finish_rental(rental.rental_id)
        self.assertEqual(len(manager.available_accounts("Game")), 1)

    def test_no_double_booking_under_parallel_requests(self):
        manager = RentalManager([Account("A-1", "Game")])
        successes = []
        failures = []
        barrier = threading.Barrier(2)

        def worker(order_id):
            barrier.wait()
            try:
                successes.append(
                    manager.issue_rental(
                        order_id=order_id,
                        game="Game",
                        duration_hours=1,
                    )
                )
            except NoAccountAvailable:
                failures.append(order_id)

        threads = [
            threading.Thread(target=worker, args=("O-1",)),
            threading.Thread(target=worker, args=("O-2",)),
        ]

        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(len(successes), 1)
        self.assertEqual(len(failures), 1)
        self.assertEqual(len(manager.active_rentals()), 1)

    def test_expired_rental_is_released(self):
        manager = RentalManager([Account("A-1", "Game")])
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)

        rental = manager.issue_rental(
            order_id="O-1",
            game="Game",
            duration_hours=1,
            now=start,
        )

        released = manager.release_expired(start + timedelta(hours=2))

        self.assertEqual([item.rental_id for item in released], [rental.rental_id])
        self.assertEqual(len(manager.available_accounts("Game")), 1)

    def test_rejects_non_positive_duration(self):
        manager = RentalManager([Account("A-1", "Game")])

        with self.assertRaises(ValueError):
            manager.issue_rental(
                order_id="O-1",
                game="Game",
                duration_hours=0,
            )


if __name__ == "__main__":
    unittest.main()
