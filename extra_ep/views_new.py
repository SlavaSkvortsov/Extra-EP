from typing import Any, Dict

import django_tables2 as tables
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from core.export_report_new import ConsumableUsageModel, ExportReport, UptimeConsumableUsageModel
from extra_ep.models import Consumable, ConsumableGroup, Player, RaidRun, Report


class ReportDetailTable(tables.Table):
    raid = tables.Column(verbose_name='Рейд')
    player = tables.Column(verbose_name='Игрок')
    item_link = tables.TemplateColumn(
        verbose_name='Предмет',
        template_code='''
{% if record.item_id %}
    <a href="#" data-wowhead="item={{ record.item_id }}&domain=ru.classic" >Item</a>
{% elif record.spell_id %}
    <a href="#" data-wowhead="spell={{ record.spell_id }}&domain=ru.classic" >Spell</a>
{% elif record.group_name %}
    {% if record.image_url %}
        <img src="{{ record.image_url }}" width="16" height="16">
    {% endif %}
    {{ record.group_name }}
{% endif %}
''',
        accessor='item_id',
    )
    amount = tables.Column(verbose_name='Использовано раз')
    uptime = tables.Column(verbose_name='Время действия %')
    points = tables.Column(verbose_name='Очков')

    class Meta:
        per_page = 200


class ReportDetailView(tables.SingleTableView):
    model = Report
    table_class = ReportDetailTable
    pk_url_kwarg = 'report_id'
    template_name = 'extra_ep/report/new_report_detail.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.warnings = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report'] = get_object_or_404(Report, id=self.kwargs['report_id'])
        context['warnings'] = self.warnings

        return context

    def get_table_data(self):
        exporter = ExportReport(self.kwargs['report_id'])
        data = exporter.process()
        self.warnings = exporter.warnings

        result = []
        for player_id, raid_run_data in data.items():
            player: Player = Player.objects.get(id=player_id)

            for raid_run_id, usage_models in raid_run_data.items():
                raid_run: RaidRun = RaidRun.objects.get(id=raid_run_id)

                for usage_model in usage_models:
                    if usage_model.points == 0:
                        continue

                    data = {}
                    if isinstance(usage_model, ConsumableUsageModel):
                        if not usage_model.times_used:
                            continue
                        data['amount'] = usage_model.times_used

                    if isinstance(usage_model, UptimeConsumableUsageModel):
                        data['uptime'] = round(usage_model.coefficient * 100, 2)

                    consumable_group = ConsumableGroup.objects.filter(id=usage_model.group_id).first()
                    image_url = consumable_group.image_url if consumable_group else None

                    result.append({
                        'player': player,
                        'raid': raid_run.raid,
                        'points': usage_model.points,
                        'item_id': (
                            Consumable.objects.get(id=usage_model.consumable_id).item_id
                            if usage_model.consumable_id else None
                        ),
                        'spell_id': (
                            Consumable.objects.get(id=usage_model.consumable_id).spell_id
                            if usage_model.consumable_id else None
                        ),
                        'group_name': consumable_group,
                        'image_url': image_url,
                        **data,
                    })

        return sorted(result, key=lambda row: row['player'].name)


class ExportReportView(DetailView):
    model = Report
    template_name = 'extra_ep/report/new_report_export_template.html'
    pk_url_kwarg = 'report_id'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data()
        context['data'] = self._get_aggregated_data()

        return context

    def _get_aggregated_data(self) -> str:
        data = ExportReport(report_id=self.object.id).process()
        rows = []

        for player_id, raid_run_data in data.items():
            player: Player = Player.objects.get(id=player_id)
            points = 0

            for raid_run_id, usage_models in raid_run_data.items():
                for usage_model in usage_models:
                    points += usage_model.points

            rows.append(f'{player.name},{points}')

        return '\n'.join(sorted(rows))
