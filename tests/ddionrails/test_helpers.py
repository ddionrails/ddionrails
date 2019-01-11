import pytest

from ddionrails.helpers import (
    jekyll_reader,
    lower_dict_names,
    render_markdown,
    script_list,
    script_list_output,
)

md_text = """
# heading

text text

* eins
* zwei

| x | y |
|---|---|
| 1 | 2 |
| 3 | 4 |
"""


class TestHelpers:
    def test_render_markdown(self):
        html = render_markdown(md_text)
        assert "<h1>" in html
        assert "<ul>" in html
        assert 'class="table"' in html

    def test_lower_dict_names(self):
        dictionary = dict(_name="NAME", othername="NAME")
        lower_dict_names(dictionary)
        assert dictionary["_name"] == "name"
        assert dictionary["othername"] == "NAME"

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_jekyll_reader(self):
        pytest.fail("Test not implemented yet")

    @pytest.mark.skip(reason="no way of currently testing this")
    def test_script_list(self):
        pytest.fail("Test not implemented yet")

    @pytest.mark.skip(reason="no way of currently testing this")
    def script_list_output(self):
        pytest.fail("Test not implemented yet")
