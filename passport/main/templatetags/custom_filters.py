from django import template

register = template.Library()


@register.filter
def get_values(dictionary, key):
    return dictionary.get(key)


@register.simple_tag
def switch_order(request, field):
    _dict = request.GET.copy()
    value = _dict.get('order_by')
    _dict['order_by'] = field
    if value:
        if value[0] == '-' and value[1:] == field:
            _dict['order_by'] = field
        elif value == field:
            _dict['order_by'] = '-' + field
        else:
            _dict['order_by'] = field
    return _dict.urlencode()
