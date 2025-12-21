# database/user/account_update.py
from typing import Optional
from database.core.db import run_query


def update_contact_info(customer_id: int, new_email: Optional[str] = None, new_phone: Optional[str] = None) -> bool:
    updates = []
    params = []

    if new_email:
        updates.append("email = %s")
        params.append(new_email)

    if new_phone:
        updates.append("phone = %s")
        params.append(new_phone)

    if not updates:
        return False

    params.append(customer_id)

    query = f"UPDATE users SET {', '.join(updates)} WHERE customer_id = %s"
    run_query(query, tuple(params), fetch=False)

    return True
