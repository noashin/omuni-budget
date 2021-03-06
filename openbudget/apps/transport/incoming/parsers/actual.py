from openbudget.apps.budgets.models import Actual, ActualItem, Budget
from openbudget.apps.transport.incoming.parsers import register
from openbudget.apps.transport.incoming.parsers.budget import BudgetParser


class ActualParser(BudgetParser):

    container_model = Actual
    item_model = ActualItem
    ITEM_ATTRIBUTES = ('amount', 'node', 'description', 'actual')
    ITEM_CLEANING_EXCLUDE = ['node', 'actual']

    def _add_to_container(self, obj, key):
        if not self.dry:
            obj['actual'] = self.container_object

    def _get_parent_template(self, container_dict):

        entity = self._set_entity()
        # set the entity also on the template container object
        # it will be used for generating a name and cleaned later
        container_dict['entity'] = entity

        if entity:
            #TODO: validate the assumption below is correct
            # assuming here there's only one budget tha contains this actual
            qs = Budget.objects.filter(
                entity=entity,
                period_start__lte=container_dict['period_start'],
                period_end__gte=container_dict['period_end']
            )[:1]

            if qs.count():
                return qs[0].template
            else:
                # try getting the latest budget prior to this actual
                qs = Budget.objects.filter(
                    entity=entity,
                    period_end__lte=container_dict['period_start']
                ).order_by('-period_end')[:1]

                if qs.count():
                    return qs[0].template
                else:
                    # try getting the earliest budget later then this actual
                    qs = Budget.objects.filter(
                        entity=entity,
                        period_start__gte=container_dict['period_end']
                    ).order_by('period_start')[:1]

                    if qs.count():
                        return qs[0].template
                    else:
                        # check for actuals and fallback to standard template
                        return super(ActualParser, self)._get_parent_template(container_dict)

register('actual', ActualParser)
