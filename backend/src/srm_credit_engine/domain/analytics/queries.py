"""Raw SQL constants for the analytical reports.

Statements are written to be portable between PostgreSQL (production, via
asyncpg) and SQLite (test suite, via aiosqlite). All bind parameters are
named (``:param``) to be consumed by :class:`sqlalchemy.text` regardless of
the backing driver.
"""

from __future__ import annotations

from typing import Final

SQL_VOLUME_BY_ASSIGNOR: Final[str] = """
SELECT
    a.id              AS assignor_id,
    a.document        AS assignor_document,
    a.legal_name      AS assignor_legal_name,
    COUNT(*)          AS receivable_count,
    SUM(r.face_value_amount)   AS total_face_value,
    SUM(s.discounted_amount)   AS total_present_value
FROM settlement AS s
JOIN receivable AS r ON r.id = s.receivable_id
JOIN assignor   AS a ON a.id = r.assignor_id
WHERE s.settled_at >= :period_start
  AND s.settled_at <  :period_end
GROUP BY a.id, a.document, a.legal_name
ORDER BY total_present_value DESC
LIMIT :row_limit
"""

SQL_PNL_BY_PRODUCT: Final[str] = """
SELECT
    p.code AS product_code,
    p.name AS product_name,
    p.settlement_currency_code AS settlement_currency,
    COUNT(*) AS settlement_count,
    SUM(r.face_value_amount * COALESCE(s.fx_rate_applied, 1))
        AS total_face_value_in_settlement_currency,
    SUM(s.discounted_amount) AS total_advanced,
    SUM(r.face_value_amount * COALESCE(s.fx_rate_applied, 1) - s.discounted_amount)
        AS total_revenue
FROM settlement   AS s
JOIN receivable   AS r ON r.id = s.receivable_id
JOIN product_type AS p ON p.code = r.product_code
WHERE s.settled_at >= :period_start
  AND s.settled_at <  :period_end
GROUP BY p.code, p.name, p.settlement_currency_code
ORDER BY total_revenue DESC
"""

SQL_AGING_BUCKETS: Final[str] = """
SELECT
    CASE
        WHEN r.due_date <  :ref_date THEN 'OVERDUE'
        WHEN r.due_date <= :d30      THEN '0_30'
        WHEN r.due_date <= :d60      THEN '31_60'
        WHEN r.due_date <= :d90      THEN '61_90'
        ELSE '90_PLUS'
    END                       AS bucket,
    COUNT(*)                  AS receivable_count,
    SUM(r.face_value_amount)  AS total_face_value
FROM receivable AS r
WHERE r.status IN ('PENDING', 'PRICED')
GROUP BY 1
ORDER BY
    CASE bucket
        WHEN 'OVERDUE' THEN 0
        WHEN '0_30'    THEN 1
        WHEN '31_60'   THEN 2
        WHEN '61_90'   THEN 3
        ELSE 4
    END
"""

SQL_FX_EXPOSURE: Final[str] = """
SELECT
    r.face_value_currency     AS currency,
    COUNT(*)                  AS receivable_count,
    SUM(r.face_value_amount)  AS total_face_value
FROM receivable AS r
WHERE r.status IN ('PENDING', 'PRICED')
GROUP BY r.face_value_currency
ORDER BY total_face_value DESC
"""

__all__ = [
    "SQL_AGING_BUCKETS",
    "SQL_FX_EXPOSURE",
    "SQL_PNL_BY_PRODUCT",
    "SQL_VOLUME_BY_ASSIGNOR",
]
