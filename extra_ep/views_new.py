from typing import Any, Dict

import django_tables2 as tables
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView

from core.export_report_new import ConsumableUsageModel, ExportReport, UptimeConsumableUsageModel
from extra_ep.models import Consumable, ConsumableGroup, Player, RaidRun, Report


class ReportDetailTable(tables.Table):
    raid = tables.Column(verbose_name='Рейд')
    player = tables.TemplateColumn(
        verbose_name='Игрок',
        template_code='''
<font {% if record.player.klass.color %}color="{{ record.player.klass.color }}"{% endif %}>
    {{ record.player }}
</font>
'''
    )
    item_link = tables.TemplateColumn(
        verbose_name='Предмет',
        template_code='''
{% if record.item_id %}
    <a href="#" data-wowhead="item={{ record.item_id }}&domain=ru.classic" >Item</a>
{% elif record.spell_id %}
    <a href="#" data-wowhead="spell={{ record.spell_id }}&domain=ru.classic" >Spell</a>
{% elif record.group_name %}
    {% if not record.group_consumables %}
        {{ record.group_name }}
    {% else %}
        <span class="tooltiptext">
            {% for consumable in record.group_consumables %}
                <div>
                    {% if consumable.item_id %}
                        <a href="#" data-wowhead="item={{ consumable.item_id }}&domain=ru.classic" >Item</a>
                    {% else %}
                        <a href="#" data-wowhead="spell={{ consumable.spell_id }}&domain=ru.classic" >Spell</a>
                    {% endif %}
                </div>
            {% endfor %}
        </span>
    {% endif %}
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
        report_id = self.kwargs['report_id']
        exporter = ExportReport(report_id)
        data = exporter.process()
        self.warnings = exporter.warnings

        result = []

        consumables = {consumable.id: consumable for consumable in Consumable.objects.all()}
        group_qs = ConsumableGroup.objects.prefetch_related('consumables').all()
        consumable_groups = {group.id: group for group in group_qs}

        raid_runs_qs = RaidRun.objects.select_related('raid').filter(report_id=report_id)
        raid_runs = {raid_run.id: raid_run for raid_run in raid_runs_qs}
        players = {player.id: player for player in Player.objects.filter(id__in=data.keys())}

        for player_id, raid_run_data in data.items():
            player = players[player_id]

            for raid_run_id, usage_models in raid_run_data.items():
                raid_run = raid_runs[raid_run_id]

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

                    consumable_group = consumable_groups.get(usage_model.group_id)
                    consumable = consumables.get(usage_model.consumable_id)

                    result.append({
                        'player': player.name,
                        'raid': raid_run.raid.name,
                        'points': usage_model.points,
                        'item_id': consumable.item_id if consumable else None,
                        'spell_id': consumable.spell_id if consumable else None,
                        'group_name': consumable_group.name if consumable_group else None,
                        'group_consumables': consumable_group.consumables.all() if consumable_group else None,
                        **data,
                    })

        return sorted(result, key=lambda row: row['player'])


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
