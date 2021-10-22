from django.template import Library, loader
from django.contrib.admin.templatetags.admin_list import result_hidden_fields, results, admin_actions

register = Library()

admin_actions = admin_actions

@register.inclusion_tag('admin/change_list.html')
def totalsum_result_list(context, cl,  unit_of_measure, template_name="Apbacode_summary_change_list.html"):

    pagination_required = (not cl.show_all or not cl.can_show_all) and cl.multi_page
    num_sorted_fields = 0

    c = {
        'cl': cl,
        'unit_of_measure': unit_of_measure,
        'result_hidden_fields': list(result_hidden_fields(cl)),
        'num_sorted_fields': num_sorted_fields,
        'results': list(results(cl)),
        'pagination_required': pagination_required
    }

    t = loader.get_template(template_name)
    return t.render(c)


