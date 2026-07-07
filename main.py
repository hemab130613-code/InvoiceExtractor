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


def extract_vendor(text: str):
    patterns = [
        r"Vendor\s*:\s*(.+)",
        r"Supplier\s*:\s*(.+)",
        r"From\s*:\s*(.+)",
        r"Billed By\s*:\s*(.+)",
        r"Issued By\s*:\s*(.+)",
    ]

    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).split("\n")[0].strip()

    return ""


def extract_currency(text: str):
    m = re.search(r"\b(USD|EUR|GBP)\b", text, re.IGNORECASE)
    if m:
        return m.group(1).upper()

    symbols = {
        "$": "USD",
        "€": "EUR",
        "£": "GBP",
    }

    for s, c in symbols.items():
        if s in text:
            return c

    return "USD"


def extract_date(text: str):
    m = re.search(r"(2026-\d{2}-\d{2})", text)
    if m:
        return m.group(1)

    return ""


def extract_amount(text: str):

    priority_patterns = [

        r"Total\s*Due\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",

        r"Amount\s*Due\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",

        r"Grand\s*Total\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",

        r"Invoice\s*Total\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",

        r"Balance\s*Due\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",

        r"Total\s*Payable\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",

        r"Total\s*[:\-]?\s*(?:USD|EUR|GBP)?\s*[$€£]?\s*([0-9]+(?:\.[0-9]+)?)",
    ]

    for p in priority_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return float(m.group(1))

    # fallback
    nums = re.findall(r"\d+\.\d{2}", text)

    if nums:
        values = [float(x) for x in nums]
        return max(values)

    nums = re.findall(r"\d+", text)

    if nums:
        values = [float(x) for x in nums]
        return max(values)

    return 0.0


@app.post("/extract", response_model=InvoiceResponse)
def extract(req: InvoiceRequest):

    text = req.text.strip()

    if text == "":
        return InvoiceResponse(
            vendor="",
            amount=0.0,
            currency="USD",
            date=""
        )

    return InvoiceResponse(
        vendor=extract_vendor(text),
        amount=extract_amount(text),
        currency=extract_currency(text),
        date=extract_date(text),
    )