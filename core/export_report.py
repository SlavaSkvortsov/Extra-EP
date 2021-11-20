import operator
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from datetime import timedelta
from functools import reduce
from itertools import chain
from typing import Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

from django.db.models import Count
from django.urls import reverse
from django.utils.functional import cached_property

from extra_ep.models import Consumable, ConsumableUsage, ConsumableUsageLimit, ConsumablesSet, Player, RaidRun


Period = namedtuple('Period', ['begin', 'end'])


@dataclass
class BaseConsumableUsageModel:
    points: int
    consumable_id: Optional[int] = None
    group_id: Optional[int] = None

    def __post_init__(self):
        if self.consumable_id is None and self.group_id is None:
            raise Exception('You should set something!!!')


@dataclass
class ConsumableUsageModel(BaseConsumableUsageModel):
    times_used: int = 0


@dataclass
class UptimeConsumableUsageModel(BaseConsumableUsageModel):
    coefficient: float = 0
    periods: List[Period] = field(default_factory=list)


ReportType = Dict[int, Dict[int, List[BaseConsumableUsageModel]]]


class Warning(NamedTuple):
    text: str
    player_id: Optional[int] = None


@dataclass
class ExportReport:
    report_id: int

    warnings: Set[Warning] = field(init=False, default_factory=set)

    _consumable_counted: Dict[int, Dict[int, int]] = field(  # Dict[player_id, Dict[consumable_id, count]]
        init=False,
        default_factory=lambda: defaultdict(lambda: defaultdict(int)),
    )

    def process(self) -> ReportType:
        result: ReportType = defaultdict(dict)

        players = set()
        players_by_raid_run = {}
        raid_runs_qs = RaidRun.objects.prefetch_related(
            'players',
        ).filter(
            report_id=self.report_id,
        ).order_by('begin')
        raid_runs = list(raid_runs_qs)

        for raid_run in raid_runs:
            raid_run_players = set(raid_run.players.all())
            players_by_raid_run[raid_run.id] = {player.id for player in raid_run_players}
            players.update(raid_run_players)

        for player in players:
            delete_url = reverse('admin:extra_ep_player_delete', args=[player.id])
            edit_url = reverse('admin:extra_ep_player_change', args=[player.id])
            buttons = f' '

            if player.role_id is None:
                self.warnings.add(Warning(text=f'У игрока {player} не указана роль!', player_id=player.id))
                continue

            if player.klass_id is None:
                self.warnings.add(Warning(text=f'У игрока {player} не указан класс!', player_id=player.id))
                continue

            required_set = self._consumable_sets.get(player.klass_id, {}).get(player.role_id)
            if required_set is None:
                self.warnings.add(Warning(
                    text=f'Для класса {player.klass} и роли {player.role} не найден набор необходимых расходников',
                ))
                continue

            consumable_uptime = self._get_player_consumable_uptime(player, required_set)
            group_uptime = self._get_player_group_uptime(player, required_set)

            for raid_run in raid_runs:
                if player.id not in players_by_raid_run[raid_run.id]:
                    continue

                result[player.id][raid_run.id] = self._raid_run_process(
                    raid_run=raid_run,
                    player=player,
                    required_set=required_set,
                    consumable_uptime=consumable_uptime,
                    group_uptime=group_uptime,
                )

        return result

    @cached_property
    def _consumable_sets(self) -> Dict[int, Dict[int, ConsumablesSet]]:
        result = defaultdict(dict)
        qs = ConsumablesSet.objects.prefetch_related('consumables', 'groups', 'groups__consumables').all()
        for consumable_set in qs:
            result[consumable_set.klass_id][consumable_set.role_id] = consumable_set

        return result

    @cached_property
    def _consumable_usage_amount(self) -> Dict[int, Dict[int, Dict[int, int]]]:
        """
        raid_run_id: player_id: consumable_id -> count
        """
        result = defaultdict(lambda: defaultdict(dict))
        query = ConsumableUsage.objects.filter(
            raid_run__report_id=self.report_id,
        ).values(
            'raid_run_id', 'player_id', 'consumable_id',
        ).annotate(
            count=Count('id'),
        )
        for row in query:
            result[row['raid_run_id']][row['player_id']][row['consumable_id']] = row['count']

        return result

    @cached_property
    def _consumable_usage_cache(self) -> Dict[int, Dict[int, List[ConsumableUsage]]]:
        result = defaultdict(lambda: defaultdict(list))

        qs = ConsumableUsage.objects.filter(
            raid_run__report_id=self.report_id,
        )
        for usage in qs:
            result[usage.player_id][usage.consumable_id].append(usage)

        return result

    @cached_property
    def _limits(self) -> Dict[int, Dict[int, int]]:
        result = defaultdict(dict)
        for limit in ConsumableUsageLimit.objects.all():
            result[limit.raid_id][limit.consumable_id] = limit.limit

        return result

    def _raid_run_process(
        self,
        raid_run: RaidRun,
        player: Player,
        required_set: ConsumablesSet,
        consumable_uptime: Dict[int, List[Period]],
        group_uptime: Dict[int, List[Period]],
    ) -> List[BaseConsumableUsageModel]:
        result: List[BaseConsumableUsageModel] = []

        all_consumables = required_set.consumables.all()
        if raid_run.is_hard_mode:
            groups_consumables = chain.from_iterable(group.consumables.all() for group in required_set.groups.all())
            all_consumables = set(all_consumables) | set(groups_consumables)

        for consumable in all_consumables:
            if consumable.usage_based_item or raid_run.is_hard_mode:
                amount = self._consumable_usage_amount.get(
                    raid_run.id, {},
                ).get(
                    player.id, {},
                ).get(consumable.id, 0)

                limit = self._limits.get(raid_run.raid_id, {}).get(consumable.id)
                if limit is not None:
                    amount = min(amount, limit)

                if consumable.is_world_buff:
                    amount = min(amount, 1)

                total_used_in_report = self._consumable_counted[player.id][consumable.id]
                if (
                    consumable.limit_over_report is not None
                    and total_used_in_report + amount > consumable.limit_over_report
                ):
                    amount = consumable.limit_over_report - total_used_in_report

                self._consumable_counted[player.id][consumable.id] += amount

                points = consumable.points_for_usage * amount
                result.append(ConsumableUsageModel(
                    points=points,
                    consumable_id=consumable.id,
                    times_used=amount,
                ))
            else:
                uptime = consumable_uptime[consumable.id]
                raid_uptime = self._get_raid_uptime(uptime, raid_run)

                points, coeff = self._get_consumable_points(
                    raid_run=raid_run,
                    raid_uptime=raid_uptime,
                    points=consumable.points_over_raid,
                    required=consumable.required,
                )

                points = int(round(points * raid_run.points_coefficient))
                result.append(UptimeConsumableUsageModel(
                    points=points,
                    consumable_id=consumable.id,
                    periods=raid_uptime,
                    coefficient=coeff,
                ))

        if not raid_run.is_hard_mode:
            for group in required_set.groups.all():
                uptime = group_uptime[group.id]
                raid_uptime = self._get_raid_uptime(uptime, raid_run)

                points, coeff = self._get_consumable_points(
                    raid_run=raid_run,
                    raid_uptime=raid_uptime,
                    points=group.points,
                    required=group.required,
                )

                points = int(round(points * raid_run.points_coefficient))
                result.append(UptimeConsumableUsageModel(
                    points=points,
                    group_id=group.id,
                    periods=raid_uptime,
                    coefficient=coeff,
                ))

        return result

    def _get_player_consumable_uptime(
        self,
        player: Player,
        required_set: ConsumablesSet,
    ) -> Dict[int, List[Period]]:
        result = {}

        for consumable in required_set.consumables.all():
            if consumable.usage_based_item:
                continue

            uptime = self._get_consumable_uptime(consumable, player)
            result[consumable.id] = uptime

        return result

    def _get_player_group_uptime(
        self,
        player: Player,
        required_set: ConsumablesSet,
    ) -> Dict[int, List[Period]]:
        result = {}

        for group in required_set.groups.all():
            uptime = self._get_group_uptime(group.consumables.all(), player)
            result[group.id] = uptime

        return result

    @staticmethod
    def _get_raid_uptime(uptime: List[Period], raid_run: RaidRun) -> List[Period]:
        raid_uptime = []

        for period in uptime:
            if period.end < raid_run.begin or period.begin > raid_run.end:
                continue

            raid_uptime.append(Period(
                begin=max(raid_run.begin, period.begin),
                end=min(raid_run.end, period.end),
            ))

        return raid_uptime

    @classmethod
    def _get_consumable_points(
        cls,
        raid_run: RaidRun,
        raid_uptime: List[Period],
        points: int,
        required: bool,
    ) -> Tuple[int, float]:
        if not raid_uptime:
            if required:
                return - points, 0
            return 0, 0

        minimum_uptime = raid_run.minimum_uptime if required else 0

        total_uptime = cls._get_total_uptime(raid_uptime)
        coefficient = total_uptime.total_seconds() / raid_run.duration.total_seconds()
        if coefficient >= raid_run.required_uptime:
            return points, coefficient

        elif coefficient >= minimum_uptime:
            a = points / (raid_run.required_uptime - minimum_uptime)
            b = - a * minimum_uptime
            return int(round(coefficient * a + b)), coefficient

        a = points / raid_run.minimum_uptime
        b = - points
        return int(round(coefficient * a + b)), coefficient

    def _get_consumable_uptime(self, consumable: Consumable, player: Player) -> List[Period]:
        uptime_list = []
        consumable_usages = self._consumable_usage_cache[player.id][consumable.id]
        for usage in consumable_usages:
            # To prevent overlapping uptimes
            self._insert_into_uptime_list(Period(usage.begin, usage.end), uptime_list)
        return uptime_list

    @staticmethod
    def _get_total_uptime(uptime: List[Period]) -> timedelta:
        return reduce(operator.add, (period.end - period.begin for period in uptime))

    def _get_group_uptime(self, consumables: Iterable[Consumable], player: Player) -> List[Period]:
        uptime: List[Period] = []
        for consumable in consumables:
            usages = self._consumable_usage_cache[player.id][consumable.id]
            for usage in usages:
                self._insert_into_uptime_list(Period(usage.begin, usage.end), uptime)

        return uptime

    @classmethod
    def _insert_into_uptime_list(
        cls,
        period: Period,
        uptime_list: List[Period],
    ) -> None:
        for i, existing_period in enumerate(uptime_list.copy()):
            if period.begin <= existing_period.end and existing_period.begin <= period.end:
                uptime_list.pop(i)
                joined_period = Period(min(period.begin, existing_period.begin), max(period.end, existing_period.end))
                cls._insert_into_uptime_list(joined_period, uptime_list)
                return

            if period.end < existing_period.begin:
                uptime_list.insert(i - 1, period)
                return

        uptime_list.insert(len(uptime_list), period)

    @cached_property
    def _all_players(self) -> Dict[int, Player]:
        return {player.id: player for player in Player.objects.all()}
