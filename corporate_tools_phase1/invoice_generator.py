"""Generate a simple invoice HTML file from JSON data."""

from __future__ import annotations

import argparse
import html
import json
from decimal import Decimal
from pathlib import Path


def money(value: Decimal | int | float | str) -> str:
    return f"{Decimal(str(value)):.2f}"


def generate_invoice(data: dict) -> str:
    items = data.get("items", [])
    tax_rate = Decimal(str(data.get("tax_rate", 0)))
    subtotal = sum(Decimal(str(item.get("quantity", 1))) * Decimal(str(item.get("unit_price", 0))) for item in items)
    tax = subtotal * tax_rate
    total = subtotal + tax

    rows = []
    for item in items:
        quantity = Decimal(str(item.get("quantity", 1)))
        unit_price = Decimal(str(item.get("unit_price", 0)))
        line_total = quantity * unit_price
        rows.append(
            "<tr>"
            f"<td>{html.escape(str(item.get('description', 'Item')))}</td>"
            f"<td>{money(quantity)}</td>"
            f"<td>{money(unit_price)}</td>"
            f"<td>{money(line_total)}</td>"
            "</tr>"
        )

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Invoice {html.escape(str(data.get('invoice_number', '')))}</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; color: #1f2328; }}
    header {{ display: flex; justify-content: space-between; gap: 24px; border-bottom: 2px solid #1f2328; padding-bottom: 20px; }}
    h1 {{ margin: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 28px; }}
    th, td {{ border-bottom: 1px solid #d0d7de; padding: 10px; text-align: left; }}
    th:last-child, td:last-child {{ text-align: right; }}
    .totals {{ margin-left: auto; margin-top: 24px; width: 280px; }}
    .totals div {{ display: flex; justify-content: space-between; padding: 6px 0; }}
    .total {{ font-weight: bold; border-top: 2px solid #1f2328; }}
  </style>
</head>
<body>
  <header>
    <section>
      <h1>Invoice</h1>
      <p>Invoice #: {html.escape(str(data.get('invoice_number', 'N/A')))}<br>Date: {html.escape(str(data.get('date', 'N/A')))}</p>
    </section>
    <section>
      <strong>{html.escape(str(data.get('business_name', 'Business')))}</strong><br>
      {html.escape(str(data.get('business_address', '')))}
    </section>
  </header>
  <p><strong>Bill To:</strong><br>{html.escape(str(data.get('client_name', 'Client')))}<br>{html.escape(str(data.get('client_address', '')))}</p>
  <table>
    <thead><tr><th>Description</th><th>Qty</th><th>Unit Price</th><th>Total</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <section class="totals">
    <div><span>Subtotal</span><span>{money(subtotal)}</span></div>
    <div><span>Tax</span><span>{money(tax)}</span></div>
    <div class="total"><span>Total</span><span>{money(total)}</span></div>
  </section>
</body>
</html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an invoice HTML file from JSON.")
    parser.add_argument("input", type=Path, help="JSON invoice data")
    parser.add_argument("--output", type=Path, default=Path("invoice.html"))
    args = parser.parse_args()

    data = json.loads(args.input.read_text(encoding="utf-8"))
    invoice = generate_invoice(data)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(invoice, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()

