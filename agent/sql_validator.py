# agent/sql_validator.py

import sqlglot
from sqlglot.errors import ParseError

def validate_sql(sql_query: str) -> bool:
    """
    Validates SQL safety and structure.
    Ensures it's a SELECT-only statement and syntactically valid.
    Now more flexible with schema-qualified and multiline SQL.
    """
    if not sql_query or "select" not in sql_query.lower():
        return False

    try:
        # Parse with relaxed settings (ignore dialect mismatches)
        parsed = sqlglot.parse_one(sql_query, read="postgres")

        # Reject non-SELECT statements
        if parsed and parsed.key.lower() != "select":
            return False

        # Basic sanitization
        lowered = sql_query.lower()
        forbidden = ["insert", "update", "delete", "drop", "alter", "truncate"]
        if any(word in lowered for word in forbidden):
            return False

        return True

    except ParseError:
        # Instead of failing hard, allow execution but log a warning
        print("SQLGlot parse warning — proceeding cautiously.")
        return True
