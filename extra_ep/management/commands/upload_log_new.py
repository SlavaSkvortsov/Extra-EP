from argparse import ArgumentParser
from os import path
from typing import Any

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError

from core.import_report_new import ReportImporter
from extra_ep.models import Report


class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any) -> None:
        log_path = r'C:\Program Files (x86)\World of Warcraft\_classic_\Logs\WoWCombatLog-split-2020-06-16T15-59-28.327Z.txt'
        user, _ = User.objects.get_or_create(email='robot@sasai.kudasai')
        report = Report.objects.create(
            uploaded_by=user,
            static=1,
        )
        with open(log_path, encoding='utf-8') as f:
            ReportImporter(report_id=report.id, log_file=f).process()

