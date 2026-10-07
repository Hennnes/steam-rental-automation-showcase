from rental_core import Account, RentalManager

manager = RentalManager(
    [
        Account("A-001", "Example Game"),
        Account("A-002", "Example Game"),
        Account("A-003", "Another Game"),
    ]
)

first = manager.issue_rental(
    order_id="ORDER-001",
    game="Example Game",
    duration_hours=2,
)
second = manager.issue_rental(
    order_id="ORDER-002",
    game="Example Game",
    duration_hours=1,
)

print("Issued:", first)
print("Issued:", second)
print("Available Example Game accounts:", manager.available_accounts("Example Game"))

manager.finish_rental(first.rental_id)

print("After first rental finished:")
print("Available Example Game accounts:", manager.available_accounts("Example Game"))
