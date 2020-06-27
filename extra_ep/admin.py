from django.contrib import admin

from extra_ep.models import Report, ItemConsumption, Combat, Boss, Raid, Player, Role, Class, ConsumablesSet, \
    Consumable, ConsumableGroup, RaidRun, ConsumableUsage


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    pass


# @admin.register(Combat)
# class CombatAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(ItemConsumption)
# class ItemConsumptionAdmin(admin.ModelAdmin):
#     pass


@admin.register(Boss)
class BossAdmin(admin.ModelAdmin):
    pass


@admin.register(Raid)
class RaidAdmin(admin.ModelAdmin):
    pass


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    pass


@admin.register(ConsumablesSet)
class ConsumablesSetAdmin(admin.ModelAdmin):
    pass


@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    pass


@admin.register(ConsumableGroup)
class ConsumableGroupAdmin(admin.ModelAdmin):
    pass


@admin.register(RaidRun)
class RaidRunAdmin(admin.ModelAdmin):
    pass


@admin.register(ConsumableUsage)
class ConsumableUsageAdmin(admin.ModelAdmin):
    pass
