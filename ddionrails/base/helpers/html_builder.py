""" Build HTML Snippets for Django views. """

from yattag import Doc


class TableBuilder:  # pylint: disable=too-few-public-methods
    """ Functions to build HTML Table snippets """

    @classmethod
    def build_table_header(cls, header_entries: list) -> str:
        """ Build a htm table header.

        Args:
            headers_entries: Text entries to appear in the header

        Returns:
            str: An html header containing the input list elements as header elements
        """

        doc, tag, text = Doc().tagtext()

        with tag("tr"):
            for header in header_entries:
                with tag("th"):
                    text(header)

        html = doc.getvalue()
        return html
