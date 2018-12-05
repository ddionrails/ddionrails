import re

from ddionrails.helpers import (
    jekyll_reader,
    render_markdown,
)

CONCEPT_RE = re.compile(r'\{([a-z0-9:\-_]*)\}', re.IGNORECASE)


class TopicRenderer:
    """
    Transform a topic document to HTML including links to the concepts.
    """

    def __init__(self, text, study):
        self.study = study
        self.text = text

    def render_text(self):
        text = CONCEPT_RE.sub(
            self._replace,
            self.text,
        )
        return render_markdown(text)

    def _replace(self, match_results):
        id_string = match_results.group(1)
        concept_link = "[%s](/concept/%s)" % (id_string, id_string)
        return concept_link


def render_topics(text, study):
    """Convenient method to use the TopicRenderer."""
    content = jekyll_reader(text)["content"]
    data = jekyll_reader(text)["data"]
    try:
        name = data["topic"]
    except:
        name = "no_name"
    try:
        label = data["label"]
    except:
        label = "missing"
    x = TopicRenderer(content, study)
    return name, label, x.render_text()
