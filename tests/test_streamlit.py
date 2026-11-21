import glob, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pytest
from streamlit.testing.v1 import AppTest

PAGES = ["streamlit_app.py"] + sorted(str(Path(p).relative_to(ROOT)) for p in glob.glob(str(ROOT / "pages" / "*.py")))


@pytest.mark.parametrize("page", PAGES)
def test_page_runs(page):
    at = AppTest.from_file(str(ROOT / page), default_timeout=120).run()
    assert not at.exception, [e.message for e in at.exception]


def test_recommender_form():
    at = AppTest.from_file(str(ROOT / "pages/5_Job_Recommender.py"), default_timeout=120).run()
    at.text_input[0].set_value("video editor")
    at.button[0].click().run()
    assert not at.exception
    assert any(m.value.startswith("**[") for m in at.markdown)
