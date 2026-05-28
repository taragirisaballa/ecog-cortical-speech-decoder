"""Command line interface for ECoG Cortical Speech Decoder."""

from __future__ import annotations

import argparse
from pathlib import Path

from .dandi import DEFAULT_DANDISET_ID, DEFAULT_VERSION, built_in_summary, fetch_assets, fetch_dandiset_summary
from .report import render_asset_inventory, render_asset_inventory_csv, render_dataset_card
from .synthetic import run_decoder_smoke_test


def main() -> None:
    parser = argparse.ArgumentParser(description="Prototype cortical speech decoding on open ECoG data.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    card_parser = subparsers.add_parser("dataset-card", help="Generate a DANDI dataset note.")
    card_parser.add_argument("--dandiset", default=DEFAULT_DANDISET_ID)
    card_parser.add_argument("--version", default=DEFAULT_VERSION)
    card_parser.add_argument("--out", default="reports/dataset_card.md")
    card_parser.add_argument(
        "--offline",
        action="store_true",
        help="Use the checked-in DANDI 000019 metadata snapshot instead of the live API.",
    )

    inventory_parser = subparsers.add_parser(
        "asset-inventory", help="Fetch DANDI asset metadata and write inventory reports."
    )
    inventory_parser.add_argument("--dandiset", default=DEFAULT_DANDISET_ID)
    inventory_parser.add_argument("--version", default=DEFAULT_VERSION)
    inventory_parser.add_argument("--out-md", default="reports/asset_inventory.md")
    inventory_parser.add_argument("--out-csv", default="reports/asset_inventory.csv")

    smoke_parser = subparsers.add_parser("smoke-decode", help="Run a synthetic decoder demo.")
    smoke_parser.add_argument("--seed", type=int, default=7)

    args = parser.parse_args()
    if args.command == "dataset-card":
        summary = built_in_summary() if args.offline else fetch_dandiset_summary(args.dandiset, args.version)
        output_path = Path(args.out)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_dataset_card(summary), encoding="utf-8")
        print(f"Wrote {output_path}")
    elif args.command == "asset-inventory":
        assets = fetch_assets(args.dandiset, args.version)
        md_path = Path(args.out_md)
        csv_path = Path(args.out_csv)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(render_asset_inventory(assets, args.dandiset, args.version), encoding="utf-8")
        csv_path.write_text(render_asset_inventory_csv(assets), encoding="utf-8")
        print(f"Wrote {md_path} and {csv_path}")
    elif args.command == "smoke-decode":
        metrics = run_decoder_smoke_test(random_state=args.seed)
        print(f"accuracy={metrics['accuracy']:.3f} chance={metrics['chance']:.3f}")


if __name__ == "__main__":
    main()
