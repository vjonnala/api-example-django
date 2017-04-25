from django import template

register = template.Library()

@register.filter(name='addclass')
def addclass(field, className):
    cur_class = field.field.widget.attrs.get('class', None)
    new_class = "%s %s" % (cur_class, className)
    return field.as_widget(attrs={"class": new_class})