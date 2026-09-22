from django import template

register = template.Library()


@register.filter
def lookup(value, key):
    if hasattr(value, 'get'):
        return value.get(key)
    return None