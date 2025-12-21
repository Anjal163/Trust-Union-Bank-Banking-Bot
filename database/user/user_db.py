from typing import Optional, List, Dict, Any
from datetime import date
from database.core.db import run_query
from database.core.connect import get_connection
from auth.db_adapter import _row_to_dict


# ---------- User ----------
def get_user_by_customer_id(customer_id: int) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT customer_id, name, email, phone, address, dob, kyc_status FROM users WHERE customer_id = %s",
            (customer_id,)
        )
        return _row_to_dict(cur, cur.fetchone())


# ---------- Accounts ----------
def get_user_accounts(customer_id: int) -> List[Dict[str, Any]]:
    q = """
        SELECT account_id, account_number, ifsc_code, branch_code,
               type, balance, status
        FROM accounts
        WHERE customer_id = %s
    """
    return run_query(q, (customer_id,), fetch=True) or []


def get_user_balance_from_db(customer_id: int, account_id: Optional[int] = None) -> float:
    if account_id:
        q = "SELECT balance FROM accounts WHERE account_id = %s AND customer_id = %s LIMIT 1"
        rows = run_query(q, (account_id, customer_id), fetch=True) or []
        return float(rows[0]["balance"]) if rows else 0.0

    q = "SELECT COALESCE(SUM(balance), 0) AS total_balance FROM accounts WHERE customer_id = %s"
    rows = run_query(q, (customer_id,), fetch=True) or []
    return float(rows[0]["total_balance"])


# ---------- Transactions ----------
def get_transactions_for_customer(customer_id: int, limit: int = 10) -> List[Dict[str, Any]]:
    q = """
        SELECT txn_id, amount, txn_type, status, description,
               transaction_reference, timestamp
        FROM transactions
        WHERE customer_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
    """
    return run_query(q, (customer_id, limit), fetch=True) or []


def transfer_money_db(
    customer_id: int,
    from_account: str,
    to_account: str,
    amount: float,
    narration: str = ""
) -> Dict[str, Any]:

    if amount <= 0:
        return {"ok": False, "message": "Invalid amount"}

    sender = run_query(
        "SELECT balance FROM accounts WHERE account_number = %s AND customer_id = %s",
        (from_account, customer_id),
        fetch=True
    ) or []

    if not sender or float(sender[0]["balance"]) < amount:
        return {"ok": False, "message": "Insufficient balance"}

    try:
        run_query(
            "UPDATE accounts SET balance = balance - %s WHERE account_number = %s AND customer_id = %s",
            (amount, from_account, customer_id)
        )
        run_query(
            "UPDATE accounts SET balance = balance + %s WHERE account_number = %s",
            (amount, to_account)
        )
        run_query(
            """
            INSERT INTO transactions
            (customer_id, sender_account_number, receiver_account_number,
             amount, txn_type, status, description)
            VALUES (%s, %s, %s, %s, 'transfer', 'completed', %s)
            """,
            (customer_id, from_account, to_account, amount, narration)
        )
        return {"ok": True, "status": "completed"}

    except Exception as e:
        return {"ok": False, "status": "failed", "message": str(e)}


# ---------- Loans ----------
def get_loan_details_from_db(customer_id: int) -> List[Dict[str, Any]]:
    q = """
        SELECT loan_id, loan_type, principal_amount,
               outstanding_balance, emi_due_date, status
        FROM loans
        WHERE customer_id = %s
    """
    return run_query(q, (customer_id,), fetch=True) or []


def get_next_emi_date(customer_id: int) -> Optional[date]:
    q = "SELECT emi_due_date FROM loans WHERE customer_id = %s LIMIT 1"
    rows = run_query(q, (customer_id,), fetch=True) or []
    return rows[0]["emi_due_date"] if rows else None


# ---------- Cards ----------
def get_user_cards(customer_id: int) -> List[Dict[str, Any]]:
    q = """
        SELECT card_id, card_type, last_4_digits,
               delivery_status, activated
        FROM cards
        WHERE customer_id = %s
    """
    return run_query(q, (customer_id,), fetch=True) or []


def get_card_limits(customer_id: int, card_id: int) -> Dict[str, Any]:
    q = """
        SELECT limit_daily, limit_monthly
        FROM cards
        WHERE card_id = %s AND customer_id = %s
    """
    rows = run_query(q, (card_id, customer_id), fetch=True) or []
    return rows[0] if rows else {"limit_daily": 0, "limit_monthly": 0}


# ---------- Complaints ----------
def raise_complaint_db(customer_id: int, category: str, description: str) -> bool:
    q = """
        INSERT INTO complaints (customer_id, category, description)
        VALUES (%s, %s, %s)
    """
    run_query(q, (customer_id, category, description))
    return True


def get_complaints_db(customer_id: int) -> List[Dict[str, Any]]:
    q = """
        SELECT complaint_id, category, status, created_on
        FROM complaints
        WHERE customer_id = %s
        ORDER BY created_on DESC
    """
    return run_query(q, (customer_id,), fetch=True) or []
