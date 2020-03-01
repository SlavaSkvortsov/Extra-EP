from django.db.models import Sum

from extra_ep.models import ItemConsumption


class ReportExporter:
    def __init__(self, report_id: int) -> None:
        self.report_id = report_id

    def export(self) -> str:
        result_qs = ItemConsumption.objects.filter(
            combat__report_id=self.report_id,
        ).values(
            'player__name',
        ).annotate(
            ep_sum=Sum('ep'),
        ).values_list('player__name', 'ep_sum')
        return '\n'.join(f'{name},{ep}' for name, ep in result_qs)
