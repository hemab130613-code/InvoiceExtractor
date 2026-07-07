from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()


class InvoiceRequest(BaseModel):
    text: str


class InvoiceResponse(BaseModel):
    vendor: str
    amount: float
    currency: str
    date: str


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    text = req.text

    if not text.strip():
        return InvoiceResponse(
            vendor="",
            amount=0,
            currency="USD",
            date=""
        )

    vendor = ""

    patterns = [
        r"Vendor[:\s]+(.+)",
        r"Supplier[:\s]+(.+)",
        r"From[:\s]+(.+)"
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            vendor = m.group(1).split("\n")[0].strip()
            break

    amount = 0

    amount_patterns = [
r"Total\s*Due[:\s\$]*([0-9]+(?:\.[0-9]+)?)",
    r"Amount\s*Due[:\s\$]*([0-9]+(?:\.[0-9]+)?)",
    r"Grand\s*Total[:\s\$]*([0-9]+(?:\.[0-9]+)?)",
    r"Invoice\s*Total[:\s\$]*([0-9]+(?:\.[0-9]+)?)",
    r"Balance\s*Due[:\s\$]*([0-9]+(?:\.[0-9]+)?)",
    r"Total[:\s\$]*([0-9]+(?:\.[0-9]+)?)"
]
    for p in amount_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            amount = float(m.group(1))
            break

    currency = "USD"

    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)

    if m:
        currency = m.group(1).upper()

    date = ""

    m = re.search(r"(2026-\d\d-\d\d)", text)

    if m:
        date = m.group(1)

    return InvoiceResponse(
        vendor=vendor,
        amount=amount,
        currency=currency,
        date=date
    )