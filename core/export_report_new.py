import operator
from collections import defaultdict, namedtuple
from dataclasses import dataclass, field
from datetime import timedelta
from functools import reduce
from typing import Dict, Iterable, List, Optional, Set, Tuple

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


@dataclass
class ExportReport:
    report_id: int

    warnings: Set[str] = field(init=False, default_factory=set)

    def process(self) -> Dict[int, Dict[int, List[BaseConsumableUsageModel]]]:
        result: Dict[int, Dict[int, List[BaseConsumableUsageModel]]] = defaultdict(dict)

        player_ids = ConsumableUsage.objects.filter(
            raid_run__report_id=self.report_id,
        ).order_by().values('player_id').distinct().values_list('player_id', flat=True)

        raid_runs = list(RaidRun.objects.filter(report_id=self.report_id))

        for player_id in set(player_ids):
            player = self._all_players[player_id]

            if player.role_id is None:
                self.warnings.add(f'У игрока {player} не указана роль!')
                continue

            if player.klass_id is None:
                self.warnings.add(f'У игрока {player} не указан класс!')
                continue

            try:
                required_set = ConsumablesSet.objects.get(
                    klass_id=player.klass_id,
                    role_id=player.role_id,
                )
            except ConsumablesSet.DoesNotExist:
                self.warnings.add(
                    f'Для класса {player.klass} и роли {player.role} не найден набор необходимых расходников',
                )
                continue

            consumable_uptime = self._get_player_consumable_uptime(player, required_set)
            group_uptime = self._get_player_group_uptime(player, required_set)

            for raid_run in raid_runs:
                result[player_id][raid_run.id] = self._raid_run_process(
                    raid_run=raid_run,
                    player=player,
                    required_set=required_set,
                    consumable_uptime=consumable_uptime,
                    group_uptime=group_uptime,
                )

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

        for consumable in required_set.consumables.all():
            if consumable.usage_based_item or raid_run.report.is_hard_mode:
                amount = ConsumableUsage.objects.filter(
                    raid_run=raid_run,
                    player=player,
                    consumable=consumable,
                ).count()

                limit_obj: ConsumableUsageLimit = ConsumableUsageLimit.objects.filter(
                    raid=raid_run.raid,
                    consumable=consumable,
                ).first()
                if limit_obj:
                    amount = min(amount, limit_obj.limit)

                points = consumable.points_for_usage * amount
                result.append(ConsumableUsageModel(
                    points=points,
                    consumable_id=consumable.id,
                    times_used=amount,
                ))
            else:
                uptime = consumable_uptime[consumable.id]
                raid_uptime = self._get_raid_uptime(uptime, raid_run)

                points, coeff = self._get_consumable_points(raid_run, raid_uptime, consumable.points_over_raid)
                if not consumable.required:
                    points = max(0, points)

                points = int(round(points * raid_run.points_coefficient))
                result.append(UptimeConsumableUsageModel(
                    points=points,
                    consumable_id=consumable.id,
                    periods=raid_uptime,
                    coefficient=coeff,
                ))

        for group in required_set.groups.all():
            uptime = group_uptime[group.id]
            raid_uptime = self._get_raid_uptime(uptime, raid_run)

            points, coeff = self._get_consumable_points(raid_run, raid_uptime, group.points_over_raid)
            if not group.required:
                points = max(0, points)

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
            uptime = self._get_group_uptime(group.consumables, player)
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
    def _get_consumable_points(cls, raid_run: RaidRun, raid_uptime: List[Period], points: int) -> Tuple[int, float]:
        if not raid_uptime:
            return - points, 0

        total_uptime = cls._get_total_uptime(raid_uptime)
        coefficient = total_uptime.total_seconds() / raid_run.duration.total_seconds()
        if coefficient >= raid_run.required_uptime:
            return points, coefficient

        elif coefficient >= raid_run.minimum_uptime:
            a = points / (raid_run.required_uptime - raid_run.minimum_uptime)
            b = - a * raid_run.minimum_uptime
            return int(round(coefficient * a + b)), coefficient

        a = points / raid_run.minimum_uptime
        b = - points
        return int(round(coefficient * a + b)), coefficient

    def _get_consumable_uptime(self, consumable: Consumable, player: Player) -> List[Period]:
        qs = ConsumableUsage.objects.filter(
            raid_run__report_id=self.report_id,
            consumable=consumable,
            player=player,
        )

        uptime_list = []
        for usage in qs:
            # To prevent overlapping uptimes
            self._insert_into_uptime_list(Period(usage.begin, usage.end), uptime_list)
        return uptime_list

    @staticmethod
    def _get_total_uptime(uptime: List[Period]) -> timedelta:
        return reduce(operator.add, (period.end - period.begin for period in uptime))

    def _get_group_uptime(self, consumables: Iterable[Consumable], player: Player) -> List[Period]:
        uptime: List[Period] = []
        for consumable in consumables:
            qs = ConsumableUsage.objects.filter(
                raid_run__report_id=self.report_id,
                consumable=consumable,
                player=player,
            )

            for usage in qs:
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
