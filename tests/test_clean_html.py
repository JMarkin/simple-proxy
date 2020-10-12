import os
import pytest

from app.utils.accept_tags import AggregateHtml


@pytest.fixture
def aggr():
    with open(
        os.path.join(os.path.dirname(__file__), "files", "uborka.html"), "rb"
    ) as f:
        raw = f.read()

    aggr = AggregateHtml(raw, [":thumbs_up:", ":sunny:"])
    return aggr


def test_clean_html(aggr):
    aggr.aggregate()
    with open(
        os.path.join(os.path.dirname(__file__), "files", "new_uborka.html"),
        "w",
    ) as f:
        f.write(str(aggr.soup))
