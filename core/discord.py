from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List
from urllib.parse import urljoin

from discord_webhook import DiscordEmbed, DiscordWebhook
from django.conf import settings
from django.urls import reverse
from django.templatetags.static import static

from core.export_report_new import BaseConsumableUsageModel, ExportReport, ReportType
from extra_ep.models import Player, RaidRun, Report


def bold(sting: str) -> str:
    return f'**{sting}**'


@dataclass
class DiscordNotification:
    report: Report

    def notify(self) -> None:
        report_data = ExportReport(report_id=self.report.id).process()
        players = self._get_players(list(report_data.keys()))
        report_data = self._regroup_report(report_data)
        raid_runs = self._get_raid_runs(list(report_data.keys()))

        embed = DiscordEmbed(
            title=f'{self.report.static} статик - {self.report.raid_name} - {self.report.raid_day}',
            description=(
                f'Начало - {self._extract_time(min(raid_run.begin for raid_run in raid_runs if raid_run.begin))}, '
                f'окончание - {self._extract_time(max(raid_run.end for raid_run in raid_runs if raid_run.end))}'
            ),
            color=0xb51cd4,
        )

        embed.set_author(
            name='EP с сайта',
            url=urljoin(settings.BASE_URL, reverse('extra_ep:report_new', kwargs={'report_id': self.report.id})),
            icon_url=urljoin(settings.BASE_URL, static('extra_ep/discord_icon.png')),
        )

        if raid_runs == 1:
            raid_run = raid_runs[0]
            embed.add_embed_field(
                name=f'⚔{raid_run.raid.name}',
                value=self._get_consumable_text(report_data[raid_run.id], players, separator=', '),
            )
        else:
            for raid_run in raid_runs:
                embed.add_embed_field(
                    name=f'⚔{raid_run.raid.name}',
                    value=self._get_consumable_text(report_data[raid_run.id], players),
                )
            self._add_total(report_data, players, embed)

        webhook = DiscordWebhook(url=settings.DISCORD_WEBHOOK_URL)
        webhook.add_embed(embed)
        webhook.execute()

    def _add_total(self, report_data: ReportType, players: List[Player], embed: DiscordEmbed) -> None:
        total = defaultdict(list)
        for raid_run_id, data in report_data.items():
            for player_id, consumables in data.items():
                total[player_id].extend(consumables)

        embed.add_embed_field(
            name=f'Всего',
            value=self._get_consumable_text(total, players),
        )

    def _get_consumable_text(
        self,
        data: Dict[int, List[BaseConsumableUsageModel]],
        players: List[Player],
        separator: str = '\n',
    ) -> str:
        player_summary = {
            player_id: sum(consumable.points for consumable in consumables) for player_id, consumables in data.items()
        }
        result = []
        for player in players:
            summary = player_summary.get(player.id)
            if summary:
                result.append(f'{player.name} - {bold(summary)}')

        return separator.join(result)

    def _get_players(self, player_ids: List[int]) -> List[Player]:
        queryset = Player.objects.filter(id__in=player_ids).select_related('klass').order_by('name')
        return list(queryset)

    def _get_raid_runs(self, raid_run_ids: List[int]) -> List[RaidRun]:
        queryset = RaidRun.objects.filter(id__in=raid_run_ids).select_related('raid').order_by('begin')
        return list(queryset)

    def _regroup_report(self, report: ReportType) -> ReportType:
        result = defaultdict(dict)
        for player_id, data in report.items():
            for raid_run_id, consumables in data.items():
                result[raid_run_id][player_id] = consumables

        return result

    def _extract_time(self, dtime: datetime) -> str:
        return dtime.strftime('%H:%M')
