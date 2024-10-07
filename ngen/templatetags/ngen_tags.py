import base64

from django import template
from django.template import Template, Context

from project import settings

register = template.Library()


@register.filter(is_safe=True)
def render_report_content(html, event):
    return Template(html).render(Context({"event": event}))


@register.simple_tag
def mail_logo():
    return encode_static(settings.LOGO_WIDE_PATH)


@register.simple_tag
def encode_static(path, encoding="base64", file_type="image"):
    """
    a template tag that returns a encoded string representation of a staticfile
    Usage::
        {% encode_static path [encoding] %}
    Examples::
        <img src="{% encode_static 'path/to/img.png' %}">
    """
    try:
        # file_path = find_static_file(MEDIA_ROOT + '/' + path)
        ext = path.split(".")[-1]
        file_str = get_file_data(path)
        return "data:{0}/{1};{2},{3}".format(
            file_type, ext, encoding, base64.b64encode(file_str).decode()
        )
    except IOError:
        return ""


@register.simple_tag
def get_encoded_logo():
    return encode_static(settings.LOGO_WIDE_PATH)


@register.simple_tag
def get_matching_report(taxonomy, lang):
    return [r for r in taxonomy.get_ancestors_reports() if r.lang == lang][:1]


def get_file_data(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
        f.close()
        return data
