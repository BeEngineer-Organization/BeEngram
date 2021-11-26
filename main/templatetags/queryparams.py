from django import template

register = template.Library()


@register.simple_tag(takes_context=True)
def update_queryparams(context, **kwargs):
    q = context["request"].GET.copy()
    for k, v in kwargs.items():
        if v is not None:
            q[k] = v
        else:
            del q[k]
    return q.urlencode()
