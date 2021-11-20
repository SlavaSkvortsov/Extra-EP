from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, TextIO, Set

from django.utils.functional import cached_property

from core.utils import parse_datetime_str
from extra_ep.models import Boss, Consumable, ConsumableUsage, Player, RaidRun, Report


class ReportImporter:
    SERVER_POSTFIX = '-РокДелар'

    def __init__(self, report_id: int, log_file: TextIO) -> None:
        self.report_id = report_id
        self.log_file = log_file

        # player_id: {consumable_id: ConsumableUsage}
        self._unfinished_consumables: Dict[int, Dict[int, ConsumableUsage]] = defaultdict(dict)

        self._player_map: Dict[str, Player] = {}
        self._player_usage_map: Dict[str, List[ConsumableUsage]] = defaultdict(list)

        self._consumable_throttling_map: Dict[Player, Dict[Consumable, List[datetime]]] = (
            defaultdict(lambda: defaultdict(list))
        )
        self._players_in_raid: Set[Player] = set()
        self._track_players = False

    def process(self) -> None:
        raid_run = None
        datetime_str = None
        # yes, I know how hacky it is, but I don't want to change type :(
        iterator = self.log_file.readlines() if hasattr(self.log_file, 'readlines') else self.log_file
        for row_raw in iterator:
            row = row_raw.split(',')
            if raid_run is None:
                raid_run = self._create_unknown_raid_run()

            datetime_str, event = row[0].split('  ')

            if event == 'ENCOUNTER_START':
                self._track_players = True
                if raid_run.begin is None:
                    raid_run.begin = parse_datetime_str(datetime_str)
                    raid_run.save()

                boss = Boss.objects.filter(encounter_id=int(row[1])).first()
                if boss is None:
                    continue

                if raid_run.raid_id is None:
                    raid_run.raid_id = boss.raid_id
                    raid_run.required_uptime = boss.raid.default_required_uptime
                    raid_run.minimum_uptime = boss.raid.default_minimum_uptime
                    raid_run.points_coefficient = boss.raid.default_points_coefficient
                    raid_run.is_hard_mode = boss.raid.default_is_hard_mode
                    raid_run.begin = parse_datetime_str(datetime_str)
                    raid_run.save()

                if raid_run.raid_id != boss.raid_id:
                    raid_run.end = parse_datetime_str(datetime_str)
                    raid_run.save()

                    raid_run = self._create_unknown_raid_run()
                    raid_run.raid_id = boss.raid_id
                    raid_run.save()

            elif event == 'ENCOUNTER_END':
                boss = Boss.objects.filter(encounter_id=int(row[1])).first()
                if boss is None:
                    continue

                time = parse_datetime_str(datetime_str)

                if boss.raid_end:
                    self._track_players = False
                    raid_run.end = time
                    raid_run.players.add(*self._players_in_raid)
                    self._players_in_raid = set()
                    raid_run.save()

                    raid_run = None

            elif event in ('SPELL_CAST_SUCCESS', 'SPELL_AURA_APPLIED'):
                self._make_consumable_usage(
                    row=row,
                    raid_run=raid_run,
                    time=parse_datetime_str(datetime_str),
                    is_aura=(event == 'SPELL_AURA_APPLIED'),
                )

            elif event == 'SPELL_AURA_REMOVED':
                self._finalize_consumable(row, parse_datetime_str(datetime_str))

            elif event == 'COMBATANT_INFO':
                self._track_combatant_auras(row, row_raw, raid_run, parse_datetime_str(datetime_str))

        if raid_run:
            if raid_run.raid_id is not None:
                raid_run.end = parse_datetime_str(datetime_str)
                raid_run.players.add(*self._players_in_raid)
                raid_run.save()
            else:
                raid_run.delete()

        self._postprocess_report()

    def _postprocess_report(self):
        for player_id, usages in self._player_usage_map.items():
            player = self._player_map.get(player_id)
            if player is None:
                continue

            for usage in usages:
                usage.player = player
                usage.save()

        qs = RaidRun.objects.filter(report_id=self.report_id).order_by('-begin')

        last_raid = qs.first()
        last_raid_end = last_raid.end if last_raid else datetime.now()

        for consumables in self._unfinished_consumables.values():
            for cons_usage in consumables.values():
                cons_usage.end = last_raid_end
                try:
                    cons_usage.save()
                except ValueError:
                    cons_usage.raid_run = last_raid
                    cons_usage.save()

        if not qs.exists():
            return

        raid_runs = list(qs)
        report = Report.objects.get(id=self.report_id)
        report.raid_day = next((raid_run.begin for raid_run in raid_runs if raid_run.begin), None)
        report.raid_name = ', '.join(sorted({str(raid_run.raid) for raid_run in raid_runs if raid_run.raid_id}))

        report.save()

    def _create_unknown_raid_run(self) -> RaidRun:
        return RaidRun.objects.create(
            report_id=self.report_id,
        )

    def _make_consumable_usage(self, row: List[Any], raid_run: RaidRun, time: datetime, is_aura: bool) -> None:
        player_name = row[2].strip('"')
        if not player_name.endswith(self.SERVER_POSTFIX):
            return

        player = self._get_or_create_player(player_name)
        if self._track_players:
            self._players_in_raid.add(player)
        consumable = self._all_consumables.get(int(row[9]))

        if consumable is None:
            return

        if is_aura and not consumable.check_by_aura_apply:
            return

        self._player_map[row[1]] = player

        aprox_usage_time = time.replace(microsecond=0)
        if aprox_usage_time in self._consumable_throttling_map[player][consumable]:
            return

        self._consumable_throttling_map[player][consumable].append(aprox_usage_time)

        existing_unfinished_usage = self._unfinished_consumables[player.id].get(consumable.id)
        if existing_unfinished_usage is not None:
            if is_aura and existing_unfinished_usage.begin + consumable.duration_timedelta > time:
                # previous aura did not end
                return

            existing_unfinished_usage.end = time
            existing_unfinished_usage.save()

        consumable_usage = ConsumableUsage(
            player=player,
            raid_run=raid_run,
            consumable=consumable,
            begin=time,
        )
        self._unfinished_consumables[player.id][consumable.id] = consumable_usage

    def _track_combatant_auras(self, row: List[Any], row_raw: str, raid_run: RaidRun, time: datetime) -> None:
        auras = row_raw[row_raw.rfind('[') + 1:]
        auras = auras.strip()
        auras = auras[:-1]

        for aura_id_str in auras.split(','):
            aura_id_str = aura_id_str.strip()
            try:
                aura_id = int(aura_id_str)
            except ValueError:
                continue

            if not aura_id:
                continue

            consumable = self._all_consumables.get(aura_id)

            if consumable is None or not consumable.is_world_buff:
                continue

            self._player_usage_map[row[1]].append(ConsumableUsage(
                raid_run=raid_run,
                consumable=consumable,
                begin=time,
                end=time,
            ))

    def _finalize_consumable(self, row: List[Any], time: datetime) -> None:
        consumable = self._all_consumables.get(int(row[9]))

        if consumable is None:
            return

        player = self._get_or_create_player(row[2].strip('"'))
        self._player_map[row[1]] = player

        unfinished_usage = self._unfinished_consumables[player.id].get(consumable.id)
        if unfinished_usage is None:
            return

        unfinished_usage.end = time
        unfinished_usage.save()
        del self._unfinished_consumables[player.id][consumable.id]

    @lru_cache(maxsize=None)
    def _get_or_create_player(self, player_name: str) -> Player:
        if '-' in player_name:
            player_name, _ = player_name.split('-')

        player, _ = Player.objects.get_or_create(name=player_name)
        return player

    @cached_property
    def _all_consumables(self) -> Dict[int, Consumable]:
        return {consumable.spell_id: consumable for consumable in Consumable.objects.all()}
