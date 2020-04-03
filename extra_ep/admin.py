from django.contrib import admin

from extra_ep.models import Report, ItemConsumption, Combat, RaidTemplate, Character


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        'uploaded_by',
        'static',
        'raid_day',
        'raid_name',
        'flushed',
    ]


@admin.register(Combat)
class CombatAdmin(admin.ModelAdmin):
    list_display = [
        'report',
        'started',
        'ended',
        'encounter',
    ]


@admin.register(ItemConsumption)
class ItemConsumptionAdmin(admin.ModelAdmin):
    search_fields = ['character', 'item_id', 'spell_id', 'ep']
    list_display = [
        'combat',
        'character',
        'spell_id',
        'item_id',
        'ep',
    ]


@admin.register(Character)
class CharacterAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_display = ['name', 'user']


@admin.register(RaidTemplate)
class RaidTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'raid_leader', 'is_base_template', 'max_total']
    autocomplete_fields = ['tanks', 'healers', 'damage_dealers']
