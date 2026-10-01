from django import template
from django.utils.html import format_html

from ..mock_data import STATUS

register = template.Library()


@register.simple_tag
def status_badge(status: str, text: str = ""):
    """Status zawsze jako ikona + tekst + kolor (sek. 12 wymagań)."""
    if status == "info":
        status_key, info = "watch", True
    else:
        status_key, info = status, False
    s = STATUS.get(status_key, STATUS["no_data"])
    label = text or ("Informacja" if info else s["label"])
    css = "info" if info else status_key
    return format_html('<span class="badge badge-{}"><span class="badge-icon" aria-hidden="true">{}</span>{}</span>',
                       css, "i" if info else s["icon"], label)


@register.filter
def pl_number(value):
    try:
        return f"{int(value):,}".replace(",", " ")
    except (TypeError, ValueError):
        return value


@register.filter
def pl_decimal(value):
    return str(value).replace(".", ",")


@register.simple_tag
def action_href(item: dict) -> str:
    """Link do czynności rozwiązującej problem (alert / obowiązek)."""
    from django.urls import reverse

    name = item.get("url")
    if name == "parameter":
        return reverse("parameter", args=[item.get("param", "Mn")])
    if name == "well":
        return reverse("well", args=[item["well"]])
    href = reverse(name)
    if name == "measurement_add" and item.get("well"):
        href += f"?well={item['well']}"
    return href
