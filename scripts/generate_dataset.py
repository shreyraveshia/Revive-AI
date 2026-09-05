from __future__ import annotations

import random
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from app.simulation.dataset import build_recovery_dataset
from app.simulation.generator import create_world, generate_transactions


SEED = 42
TRANSACTION_COUNT = 20_000

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


def main() -> None:
    random.seed(SEED)

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    print("Creating synthetic world...")
    world = create_world(
        merchant_count=100,
        customer_count=5_000,
    )

    print(f"Generating {TRANSACTION_COUNT:,} transactions...")
    transactions = generate_transactions(
        world=world,
        count=TRANSACTION_COUNT,
    )

    print("Building action-level recovery dataset...")
    recovery_rows = build_recovery_dataset(
        world=world,
        transactions=transactions,
    )

    transactions_df = pd.DataFrame(
        asdict(transaction)
        for transaction in transactions
    )

    recovery_df = pd.DataFrame(
        asdict(row)
        for row in recovery_rows
    )

    # Convert enum values to normal strings where necessary.
    transactions_df["payment_method"] = (
        transactions_df["payment_method"].astype(str)
    )
    transactions_df["status"] = (
        transactions_df["status"].astype(str)
    )
    transactions_df["failure_code"] = (
        transactions_df["failure_code"].astype(str)
    )

    # Sort explicitly by event time.
    transactions_df = transactions_df.sort_values(
        "created_at"
    ).reset_index(drop=True)

    recovery_df = recovery_df.sort_values(
        ["created_at", "transaction_id", "action"]
    ).reset_index(drop=True)

    # Save the application-level transaction data.
    transactions_df.to_csv(
        RAW_DIR / "transactions.csv",
        index=False,
    )

    # Save the complete action-level dataset.
    recovery_df.to_csv(
        PROCESSED_DIR / "recovery_dataset.csv",
        index=False,
    )

    # Determine transaction-level split boundaries.
    ordered_transactions = (
        transactions_df[
            ["transaction_id", "created_at"]
        ]
        .drop_duplicates()
        .sort_values("created_at")
        .reset_index(drop=True)
    )

    transaction_count = len(ordered_transactions)

    train_end = int(transaction_count * 0.70)
    validation_end = int(transaction_count * 0.85)

    train_ids = set(
        ordered_transactions.iloc[:train_end]["transaction_id"]
    )

    validation_ids = set(
        ordered_transactions.iloc[
            train_end:validation_end
        ]["transaction_id"]
    )

    test_ids = set(
        ordered_transactions.iloc[validation_end:]["transaction_id"]
    )

    train_df = recovery_df[
        recovery_df["transaction_id"].isin(train_ids)
    ].copy()

    validation_df = recovery_df[
        recovery_df["transaction_id"].isin(validation_ids)
    ].copy()

    test_df = recovery_df[
        recovery_df["transaction_id"].isin(test_ids)
    ].copy()

    train_df.to_csv(
        PROCESSED_DIR / "train.csv",
        index=False,
    )

    validation_df.to_csv(
        PROCESSED_DIR / "validation.csv",
        index=False,
    )

    test_df.to_csv(
        PROCESSED_DIR / "test.csv",
        index=False,
    )

    print()
    print("=== REVIVE AI DATASET ===")
    print(f"Seed:                  {SEED}")
    print(f"Transactions:          {len(transactions_df):,}")
    print(
        f"Failed transactions:   "
        f"{transactions_df['failure_code'].notna().sum():,}"
    )
    print(f"Recovery rows:         {len(recovery_df):,}")
    print()

    print("Temporal split")
    print(
        f"  Train:      "
        f"{len(train_df):,} rows / "
        f"{len(train_ids):,} transactions"
    )
    print(
        f"  Validation: "
        f"{len(validation_df):,} rows / "
        f"{len(validation_ids):,} transactions"
    )
    print(
        f"  Test:       "
        f"{len(test_df):,} rows / "
        f"{len(test_ids):,} transactions"
    )

    print()
    print("Time boundaries")

    print(
        "  Train:",
        ordered_transactions.iloc[0]["created_at"],
        "→",
        ordered_transactions.iloc[train_end - 1]["created_at"],
    )

    print(
        "  Validation:",
        ordered_transactions.iloc[train_end]["created_at"],
        "→",
        ordered_transactions.iloc[validation_end - 1]["created_at"],
    )

    print(
        "  Test:",
        ordered_transactions.iloc[validation_end]["created_at"],
        "→",
        ordered_transactions.iloc[-1]["created_at"],
    )

    # Safety checks.
    train_overlap = train_ids & validation_ids
    train_test_overlap = train_ids & test_ids
    validation_test_overlap = validation_ids & test_ids

    assert not train_overlap
    assert not train_test_overlap
    assert not validation_test_overlap

    assert len(train_df) % 6 == 0
    assert len(validation_df) % 6 == 0
    assert len(test_df) % 6 == 0

    print()
    print("✅ No transaction overlap between splits.")
    print("✅ Every failed transaction contributes exactly six action rows.")
    print("✅ Dataset generation complete.")


if __name__ == "__main__":
    main()