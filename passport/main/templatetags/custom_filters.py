from django import template

register = template.Library()


@register.filter
def get_values(dictionary, key):
    return dictionary.get(key)
