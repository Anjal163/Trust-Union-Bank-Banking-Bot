# database/user/document_db.py

import os
from typing import Optional
from datetime import datetime
from database.core.db import run_query
from auth.utils.email_service import send_email
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def store_user_document(customer_id: int, doc_type: str, content: str) -> Optional[int]:
    base_dir = "/secure_uploads"
    user_dir = os.path.join(base_dir, str(customer_id))
    _ensure_dir(user_dir)

    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    file_name = f"{doc_type}_{timestamp}.txt"
    file_path = os.path.join(user_dir, file_name)

    try:
        with open(file_path, "w", encoding="utf-8") as fh:
            fh.write(content)

        query = """
            INSERT INTO kyc_docs (customer_id, doc_type, file_path, uploaded_at)
            VALUES (%s, %s, %s, NOW())
            RETURNING kyc_id
        """
        res = run_query(query, (customer_id, doc_type, file_path), fetch=True)
        return res[0]["kyc_id"] if res else None

    except Exception:
        return None


def _build_statement_pdf(customer_id: int, output_path: str, period_days: int = 30) -> bool:
    query = """
        SELECT transaction_reference, timestamp, sender_account_number,
               receiver_account_number, amount, txn_type, status, description
        FROM transactions
        WHERE customer_id = %s
          AND timestamp >= (NOW() - INTERVAL '%s days')
        ORDER BY timestamp DESC
        LIMIT 500
    """
    rows = run_query(query, (customer_id, period_days), fetch=True) or []

    try:
        _ensure_dir(os.path.dirname(output_path))
        c = canvas.Canvas(output_path, pagesize=A4)
        width, height = A4

        margin = 15 * mm
        y = height - margin

        c.setFont("Helvetica-Bold", 14)
        c.drawString(margin, y, "Trust Union Bank - Account Statement")
        y -= 10 * mm

        c.setFont("Helvetica", 10)
        c.drawString(margin, y, f"Customer ID: {customer_id}")
        c.drawString(width / 2, y, f"Generated: {datetime.utcnow():%Y-%m-%d %H:%M UTC}")
        y -= 8 * mm

        c.setFont("Helvetica-Bold", 9)
        c.drawString(margin, y, "Date")
        c.drawString(margin + 70 * mm, y, "Description")
        c.drawString(margin + 150 * mm, y, "Amount")
        y -= 6 * mm

        c.setFont("Helvetica", 9)

        if not rows:
            c.drawString(margin, y, "No transactions available.")
        else:
            for r in rows:
                if y < margin + 20:
                    c.showPage()
                    y = height - margin

                date_str = r["timestamp"].strftime("%Y-%m-%d") if r.get("timestamp") else "-"
                desc = (r.get("description") or r.get("transaction_reference") or "")[:60]
                amt = r.get("amount") or 0.0

                c.drawString(margin, y, date_str)
                c.drawString(margin + 70 * mm, y, desc)
                c.drawRightString(margin + 190 * mm, y, f"₹{amt:,.2f}")
                y -= 6 * mm

        c.showPage()
        c.save()
        return True

    except Exception:
        return False


def generate_statement_pdf_link(customer_id: int, period_days: int = 30) -> Optional[str]:
    base_dir = "/secure_uploads"
    user_dir = os.path.join(base_dir, str(customer_id), "statements")
    _ensure_dir(user_dir)

    filename = f"statement_{period_days}d_{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}.pdf"
    file_path = os.path.join(user_dir, filename)

    if not _build_statement_pdf(customer_id, file_path, period_days):
        return None

    return f"https://trustunionbank.com/secure_statements/{customer_id}/{filename}"


def send_statement_via_email(customer_id: int, period_days: int = 30) -> bool:
    rows = run_query("SELECT email FROM users WHERE customer_id = %s", (customer_id,), fetch=True)
    if not rows or not rows[0].get("email"):
        return False

    email = rows[0]["email"]
    link = generate_statement_pdf_link(customer_id, period_days)
    if not link:
        return False

    subject = "Your Account Statement - Trust Union Bank"
    html_body = (
        "<p>Dear Customer,</p>"
        "<p>Your account statement is ready.</p>"
        f"<p><a href='{link}'>Download Statement</a></p>"
        "<p>— Trust Union Bank</p>"
    )

    return bool(send_email(to_email=email, subject=subject, html_body=html_body))
