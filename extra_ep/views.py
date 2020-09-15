import codecs
from typing import Any, Dict

import chardet
import django_tables2 as tables
from django.db.models import QuerySet, Sum, Count, F
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import RedirectView, DetailView, UpdateView, CreateView
from django_tables2 import A

from core.export_report import ReportExporter
from core.import_report import ReportImporter
from core.import_report_new import ReportImporter as ReportImporterNew
from extra_ep.forms import ChangeExportedForm, UploadFile
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
    template_name = 'extra_ep/report/item_consumption_list_template.html'

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
    template_name = 'extra_ep/report/combat_list_template.html'

    def __init__(self) -> None:
        super().__init__()
        self.report = None

    def get_queryset(self) -> QuerySet:
        self.report = get_object_or_404(Report, id=self.kwargs.get('report_id'))
        return super().get_queryset().filter(report=self.report)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['report'] = self.report
        context['change_exported_from'] = ChangeExportedForm(instance=self.report)
        return context


class ReportTable(tables.Table):
    raid_name = tables.LinkColumn(
        viewname='extra_ep:report_new',
        text=lambda report: report.raid_name,
        kwargs={'report_id': A('pk')},
    )

    class Meta:
        model = Report
        fields = ('raid_name', 'static', 'raid_day', 'flushed', 'uploaded_by', 'created_at')


class ReportListView(tables.SingleTableView):
    model = Report
    table_class = ReportTable
    template_name = 'extra_ep/report/report_list_template.html'


class ItemConsumptionTotalTable(ItemConsumptionTable):
    count = tables.Column(verbose_name='Кол-во')
    used_at = None

    class Meta:
        model = ItemConsumption
        per_page = 100
        fields = ('player', 'item_link', 'count', 'ep')


class ItemConsumptionTotalListView(tables.SingleTableView):
    model = ItemConsumption
    table_class = ItemConsumptionTotalTable
    template_name = 'extra_ep/report/item_consumption_total_template.html'

    def __init__(self) -> None:
        super().__init__()
        self.report = None

    def get_queryset(self) -> QuerySet:
        self.report = get_object_or_404(Report, id=self.kwargs.get('report_id'))
        qs = ItemConsumption.objects.filter(
            combat__report=self.report,
        ).order_by(
            'player__name',
            'item_id',
        ).values(
            'player__name',
            'item_id',
        ).annotate(
            ep=Sum('ep'),
            count=Count('id'),
            player=F('player__name'),
        )
        return qs

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['report'] = self.report
        return context


class MainRedirectView(RedirectView):
    pattern_name = 'extra_ep:report_list'


class ExportReportView(DetailView):
    model = Report
    template_name = 'extra_ep/report/report_export_template.html'
    pk_url_kwarg = 'report_id'

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data()
        context['data'] = ReportExporter(report_id=self.object.id).export()
        return context


class ChangeExportedView(UpdateView):
    model = Report
    form_class = ChangeExportedForm
    pk_url_kwarg = 'report_id'

    def get_success_url(self):
        return reverse('extra_ep:combat_list', kwargs={'report_id': self.object.id})


class CreateReportView(CreateView):
    form_class = UploadFile
    template_name = 'extra_ep/report/report_create_template.html'

    def get_success_url(self):
        return reverse('extra_ep:report_new', kwargs={'report_id': self.object.id})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        result = super().form_valid(form)

        chardet_result = chardet.detect(form.files['log_file'].file.read(1000))
        encoding = chardet_result['encoding']
        form.files['log_file'].file.seek(0)

        new_importer = ReportImporterNew(
            report_id=self.object.id,
            log_file=codecs.iterdecode(form.files['log_file'].file, encoding),
        )
        new_importer.process()

        return result
