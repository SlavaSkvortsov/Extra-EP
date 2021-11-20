from django.contrib import admin
from django.http import HttpResponseRedirect

from extra_ep.models import (
    Boss, Class,  Consumable, ConsumableGroup, ConsumableUsage, ConsumableUsageLimit, ConsumablesSet,
    Player, Raid, RaidRun, Report, Role
)


class RaidRunInline(admin.TabularInline):
    model = RaidRun
    autocomplete_fields = ('players',)
    extra = 0


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    inlines = [
        RaidRunInline,
    ]
    list_filter = ('static', 'flushed')
    search_fields = ('raid_name',)


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
    search_fields = ('name', 'klass__name', 'role__name')

    def response_delete(self, request, obj_display, obj_id):
        next_url = request.POST.get('next', None)
        if next_url:
            return HttpResponseRedirect(next_url)

        return super().response_delete(request, obj_display, obj_id)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(ConsumablesSet)
class ConsumablesSetAdmin(admin.ModelAdmin):
    autocomplete_fields = ('consumables', 'groups')
    list_filter = ('klass', 'role')
    search_fields = ('consumables__name', 'groups__name')


class LimitInline(admin.TabularInline):
    model = ConsumableUsageLimit


@admin.register(Consumable)
class ConsumableAdmin(admin.ModelAdmin):
    inlines = [
        LimitInline,
    ]
    search_fields = ('spell_id', 'item_id', 'name', 'points_for_usage')
    list_filter = ('usage_based_item',)
    list_display = (
        'name',
        'usage_based_item',
        'points_for_usage',
        'points_over_raid',
        'required',
    )


@admin.register(ConsumableGroup)
class ConsumableGroupAdmin(admin.ModelAdmin):
    autocomplete_fields = ('consumables',)
    search_fields = ('name', 'consumables__name')


@admin.register(RaidRun)
class RaidRunAdmin(admin.ModelAdmin):
    autocomplete_fields = ('players',)


@admin.register(ConsumableUsage)
class ConsumableUsageAdmin(admin.ModelAdmin):
    search_fields = ('raid_run__report__raid_name', 'consumable__name', 'player__name')
    list_filter = ('raid_run__report', 'consumable', 'player')
