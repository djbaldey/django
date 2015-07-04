from django import template

register = template.Library()

@register.filter(is_safe=False)
def has_perm(user, perm):
    return user.has_perm(perm)

@register.filter(is_safe=False)
def has_module_perms(user, perm):
    return user.has_module_perms(perm)
