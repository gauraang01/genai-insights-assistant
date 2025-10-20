from agent.sql_validator import validate_sql

def test_validate_sql_allows_select():
    assert validate_sql("SELECT * FROM fct_orders LIMIT 5;")

def test_validate_sql_rejects_update():
    assert not validate_sql("UPDATE fct_orders SET x=1;")
