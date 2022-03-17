"""Custom filters for metadata rendering."""
import markdown
from django import template
from django.template.defaultfilters import stringfilter

register: template.Library = template.Library()


@register.filter()
@stringfilter
def markdown_string(value: str) -> str:
    """Render markdown as HTML"""
    return markdown.markdown(value, extensions=["markdown.extensions.fenced_code"])
