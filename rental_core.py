from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Iterable
import itertools


@dataclass
class Account:
    account_id: str
    game: str
    status: str = "available"


@dataclass
class Rental:
    rental_id: str
    account_id: str
    order_id: str
    game: str
    created_at: datetime
    expires_at: datetime
    status: str = "active"


class NoAccountAvailable(RuntimeError):
    pass


class RentalManager:
    """Small, sanitized domain core extracted from the production design."""

    def __init__(self, accounts: Iterable[Account]):
        self._accounts = {account.account_id: account for account in accounts}
        self._rentals: dict[str, Rental] = {}
        self._lock = RLock()
        self._sequence = itertools.count(1)

    def issue_rental(
        self,
        *,
        order_id: str,
        game: str,
        duration_hours: float,
        now: datetime | None = None,
    ) -> Rental:
        if duration_hours <= 0:
            raise ValueError("duration_hours must be positive")

        created_at = now or datetime.now(timezone.utc)

        # Search + reserve + rental creation are one atomic operation.
        # This prevents two concurrent orders from receiving the same account.
        with self._lock:
            account = next(
                (
                    item
                    for item in self._accounts.values()
                    if item.game == game and item.status == "available"
                ),
                None,
            )
            if account is None:
                raise NoAccountAvailable(f"no free account for {game}")

            account.status = "rented"
            rental_id = f"R{next(self._sequence):06d}"
            rental = Rental(
                rental_id=rental_id,
                account_id=account.account_id,
                order_id=order_id,
                game=game,
                created_at=created_at,
                expires_at=created_at + timedelta(hours=duration_hours),
            )
            self._rentals[rental_id] = rental
            return rental

    def finish_rental(self, rental_id: str) -> Rental:
        with self._lock:
            rental = self._rentals[rental_id]
            if rental.status != "active":
                return rental

            rental.status = "finished"
            self._accounts[rental.account_id].status = "available"
            return rental

    def release_expired(self, now: datetime | None = None) -> list[Rental]:
        current = now or datetime.now(timezone.utc)
        released: list[Rental] = []

        with self._lock:
            for rental in self._rentals.values():
                if rental.status == "active" and rental.expires_at <= current:
                    rental.status = "finished"
                    self._accounts[rental.account_id].status = "available"
                    released.append(rental)

        return released

    def available_accounts(self, game: str | None = None) -> list[Account]:
        with self._lock:
            return [
                account
                for account in self._accounts.values()
                if account.status == "available"
                and (game is None or account.game == game)
            ]

    def active_rentals(self) -> list[Rental]:
        with self._lock:
            return [
                rental
                for rental in self._rentals.values()
                if rental.status == "active"
            ]
