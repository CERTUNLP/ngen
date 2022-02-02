from django import template
from django.template import Template, Context

register = template.Library()


@register.filter(is_safe=True)
def render_report_content(html, event):
    return Template(html).render(Context({'event': event}))
