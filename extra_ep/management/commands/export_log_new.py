from argparse import ArgumentParser
from os import path
from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from core.export_report_new import ExportReport
from core.import_report_new import ReportImporter
from extra_ep.models import Report


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> None:
        report = Report.objects.order_by('-id').first()
        result = ExportReport(report.id).process()
        print(result)
