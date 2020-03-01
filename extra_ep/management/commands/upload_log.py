from argparse import ArgumentParser
from os import path
from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from core.export_report import ReportExporter
from core.import_report import ReportImporter
from extra_ep.models import Report


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument('log_path', type=str)
        parser.add_argument('static', type=int)

    def handle(self, *args: Any, **options: Any) -> None:
        if 'log_path' not in options:
            raise CommandError('log_path have to be specified')

        if 'static' not in options:
            raise CommandError('static have to be specified')

        log_path = options['log_path']
        if not path.isfile(log_path):
            raise CommandError('Incorrect log path')

        user, _ = User.objects.get_or_create(email='robot@sasai.kudasai')
        report = Report.objects.create(
            uploaded_by=user,
            static=options['static'],
        )
        with open(log_path, encoding='utf-8') as f:
            ReportImporter(report_id=report.id, log_file=f).process()

        print(ReportExporter(report.id).export())
