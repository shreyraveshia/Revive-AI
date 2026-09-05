from collections import Counter

from app.simulation.generator import create_world, generate_transactions


def main() -> None:
    world = create_world()

    transactions = generate_transactions(
        world=world,
        count=10_000,
    )

    total = len(transactions)

    successful = sum(
        1
        for tx in transactions
        if tx.status == "success"
    )

    failed = total - successful

    payment_methods = Counter(
        tx.payment_method
        for tx in transactions
    )

    failure_codes = Counter(
        tx.failure_code
        for tx in transactions
        if tx.failure_code is not None
    )

    unique_customers = len(
        {tx.customer_id for tx in transactions}
    )

    unique_merchants = len(
        {tx.merchant_id for tx in transactions}
    )

    average_amount_paise = (
        sum(tx.amount_paise for tx in transactions)
        / total
    )

    print("=== REVIVE AI SIMULATION REPORT ===")
    print(f"Merchants in world:     {len(world.merchants):,}")
    print(f"Customers in world:     {len(world.customers):,}")
    print(f"Transactions:           {total:,}")
    print(f"Unique merchants used:  {unique_merchants:,}")
    print(f"Unique customers used:  {unique_customers:,}")
    print()

    print("Transaction outcomes")
    print(f"  Successful: {successful:,} ({successful / total:.2%})")
    print(f"  Failed:     {failed:,} ({failed / total:.2%})")
    print()

    print("Payment methods")
    for method, count in payment_methods.most_common():
        print(f"  {method}: {count:,} ({count / total:.2%})")
    print()

    print("Failure codes")
    for code, count in failure_codes.most_common():
        print(f"  {code}: {count:,} ({count / failed:.2%})")
    print()

    print(
        f"Average transaction value: "
        f"₹{average_amount_paise / 100:,.2f}"
    )


if __name__ == "__main__":
    main()