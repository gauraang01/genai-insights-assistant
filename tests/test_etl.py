# tests/test_etl.py
import os
import time
from scripts import etl

def test_run_etl_creates_output(tmp_path):
    os.environ["OUTPUT_DIR"] = str(tmp_path)
    res = etl.run_etl()
    # check that output path exists
    assert "output_path" in res
    assert os.path.exists(res["output_path"])
    # agg_preview should be non-empty
    assert isinstance(res["agg_preview"], list)
    assert len(res["agg_preview"]) >= 1
