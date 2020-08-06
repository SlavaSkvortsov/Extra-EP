from django.contrib import admin

from extra_ep.models import (
    Boss, Class, Consumable, ConsumableGroup, ConsumableUsage, ConsumablesSet, Player, Raid,
    RaidRun, Report, Role,
    Combat,
    ItemConsumption
)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_filter = ('static', 'flushed')
    search_fields = ('raid_name',)


@admin.register(Combat)
class CombatAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemConsumption)
class ItemConsumptionAdmin(admin.ModelAdmin):
    pass


@admin.register(Boss)
class BossAdmin(admin.ModelAdmin):
    list_filter = ('raid',)
    search_fields = ('name', 'raid')


@admin.register(Raid)
class RaidAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_filter = ('klass', 'role')
    search_fields = ('name', 'klass', 'role')


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(ConsumablesSet)
class ConsumablesSetAdmin(admin.ModelAdmin):
    list_filter = ('klass', 'role')
    search_fields = ('consumables__name', 'groups__name')


@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    search_fields = ('spell_id', 'spell_name', 'name', 'points')
    list_filter = ('points_for_usage',)


@admin.register(ConsumableGroup)
class ConsumableGroupAdmin(admin.ModelAdmin):
    search_fields = ('name', 'consumables__name')


@admin.register(RaidRun)
class RaidRunAdmin(admin.ModelAdmin):
    pass


@admin.register(ConsumableUsage)
class ConsumableUsageAdmin(admin.ModelAdmin):
    search_fields = ('raid_run__report__raid_name', 'consumable__name', 'player__name')
    list_filter = ('raid_run__report', 'consumable', 'player')
