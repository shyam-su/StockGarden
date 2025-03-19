from django import template
print("Loading dict_lookup.py")  #
register = template.Library()

@register.filter
def lookup(dict_obj, key):
    return dict_obj.get(key)