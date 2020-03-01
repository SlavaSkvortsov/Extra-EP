from django.contrib import admin

from extra_ep.models import Report, ItemConsumption, Combat


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    pass


@admin.register(Combat)
class CombatAdmin(admin.ModelAdmin):
    pass


@admin.register(ItemConsumption)
class ItemConsumptionAdmin(admin.ModelAdmin):
    pass
