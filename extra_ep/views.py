from typing import Any, Dict

import django_tables2 as tables
from django.db.models import QuerySet, Sum
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django_tables2 import A

from extra_ep.models import Combat, ItemConsumption, Report


class ItemConsumptionTable(tables.Table):
    item_link = tables.TemplateColumn(
        verbose_name='Предмет',
        template_code='<a href="#" data-wowhead="item={{ record.item_id }}&domain=ru.classic" >Item</a>',
        accessor='item_id',
    )

    class Meta:
        model = ItemConsumption
        fields = ('player', 'item_link', 'used_at', 'ep')
        per_page = 100


class ItemConsumptionListView(tables.SingleTableView):
    model = ItemConsumption
    table_class = ItemConsumptionTable
    template_name = 'extra_ep/item_consumption_list_template.html'

    def __init__(self) -> None:
        super().__init__()
        self.combat = None

    def get_queryset(self) -> QuerySet:
        self.combat = get_object_or_404(Combat, id=self.kwargs.get('combat_id'))
        return super().get_queryset().filter(combat=self.combat)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['combat'] = self.combat
        return context


class CombatTable(tables.Table):
    encounter = tables.LinkColumn(
        viewname='extra_ep:item_consumption_list',
        text=lambda combat: combat.encounter,
        kwargs={'combat_id': A('pk')},
    )

    class Meta:
        model = Combat
        fields = ('encounter', 'started', 'ended')
        per_page = 100


class CombatListView(tables.SingleTableView):
    model = Combat
    table_class = CombatTable
    template_name = 'extra_ep/combat_list_template.html'

    def __init__(self) -> None:
        super().__init__()
        self.report = None

    def get_queryset(self) -> QuerySet:
        self.report = get_object_or_404(Report, id=self.kwargs.get('report_id'))
        return super().get_queryset().filter(report=self.report)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['report'] = self.report
        return context


class ReportTable(tables.Table):
    raid_name = tables.LinkColumn(
        viewname='extra_ep:combat_list',
        text=lambda report: report.raid_name,
        kwargs={'report_id': A('pk')},
    )

    class Meta:
        model = Report
        fields = ('raid_name', 'static', 'raid_day', 'flushed', 'uploaded_by', 'created_at')


class ReportListView(tables.SingleTableView):
    model = Report
    table_class = ReportTable
    template_name = 'extra_ep/report_list_template.html'


class ItemConsumptionTotalTable(tables.Table):
    class Meta:
        model = ItemConsumption
        per_page = 100
        fields = ('player__name', 'ep')


class ItemConsumptionTotalListView(tables.SingleTableView):
    model = ItemConsumption
    table_class = ItemConsumptionTotalTable
    template_name = 'extra_ep/item_consumption_total_template.html'

    def __init__(self) -> None:
        super().__init__()
        self.report = None

    def get_queryset(self) -> QuerySet:
        self.report = get_object_or_404(Report, id=self.kwargs.get('report_id'))
        qs = ItemConsumption.objects.filter(
            combat__report=self.report,
        ).values(
            'player__name',
        ).annotate(
            ep=Sum('ep'),
        )
        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['report'] = self.report
        return context


class MainRedirectView(RedirectView):
    pattern_name = 'extra_ep:report_list'
