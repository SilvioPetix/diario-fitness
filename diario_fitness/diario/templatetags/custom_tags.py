from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, '')


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, '')