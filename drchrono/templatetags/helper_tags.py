from django import template

from drchrono.models import CheckOutSurveyResponse

register = template.Library()


@register.filter(name='addclass')
def addclass(field, className):
    cur_class = field.field.widget.attrs.get('class', None)
    new_class = "%s %s" % (cur_class, className)
    return field.as_widget(attrs={"class": new_class})

@register.simple_tag
def get_row_class_for_response_answer(answer):
    lookup_table = {
        CheckOutSurveyResponse.ANSWER_DEFINITELY: 'success',
        CheckOutSurveyResponse.ANSWER_SOMEWHAT: 'warning',
        CheckOutSurveyResponse.ANSWER_NO: 'danger',
    }
    return lookup_table.get(answer)