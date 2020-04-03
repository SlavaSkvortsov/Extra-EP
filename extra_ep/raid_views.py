from enum import Enum
from itertools import zip_longest

import django_tables2 as tables
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Count, Subquery, OuterRef, F
from django.db.models.functions import Coalesce
from django.forms import ModelMultipleChoiceField
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DetailView, FormView, UpdateView
from django_select2.forms import Select2MultipleWidget, ModelSelect2MultipleWidget

from extra_ep.models import RaidTemplate, Character


class CreateOrUpdateStaticForm(forms.ModelForm):
    raid_leader = forms.ModelChoiceField(label='РЛ', queryset=Character.objects.all())
    max_total = forms.ChoiceField(choices=((20, 20), (40, 40)), label='Максимум игроков')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['raid_leader'].queryset = Character.objects.filter(
            user=self.request.user,
        )

    class Meta:
        model = RaidTemplate
        fields = (
            'name',
            'raid_leader',
            'tanks',
            'max_tanks',
            'healers',
            'max_healers',
            'damage_dealers',
            'max_damage_dealers',
            'max_total',
        )
        widgets = {
            'tanks': ModelSelect2MultipleWidget(
                model=Character,
                search_fields=['name__icontains'],
                attrs={'style': 'width: 200px;'},
            ),
            'healers': ModelSelect2MultipleWidget(
                model=Character,
                search_fields=['name__icontains'],
                attrs={'style': 'width: 200px;'},
            ),
            'damage_dealers': ModelSelect2MultipleWidget(
                model=Character,
                search_fields=['name__icontains'],
                attrs={'style': 'width: 200px;'},
            ),
        }

    def save(self, commit=True):
        self.instance.is_base_template = True
        return super().save(commit)


class AddStaticView(LoginRequiredMixin, CreateView):
    form_class = CreateOrUpdateStaticForm
    template_name = 'extra_ep/raids/static_properties.html'
    model = RaidTemplate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание статика'
        return context

    def get_success_url(self):
        return reverse('extra_ep:edit_static', kwargs={'pk': self.object.id})


class ChangeStaticView(LoginRequiredMixin, UpdateView):
    form_class = CreateOrUpdateStaticForm
    template_name = 'extra_ep/raids/static_properties.html'
    model = RaidTemplate

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Редактирование статика'
        return context

    def get_success_url(self):
        return reverse('extra_ep:edit_static', kwargs={'pk': self.object.id})


class StaticListTable(tables.Table):
    name = tables.Column(
        linkify=('extra_ep:edit_static', {'pk': tables.A('id')}),
        verbose_name='Название'
    )
    ppl_total = tables.Column('Всего людей')

    class Meta:
        model = RaidTemplate
        fields = ('name', 'raid_leader', 'max_total', 'ppl_total')


class StaticListView(tables.SingleTableView):
    template_name = 'extra_ep/raids/static_list.html'
    table_class = StaticListTable
    model = RaidTemplate

    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.annotate(
            count_tanks=Subquery(
                RaidTemplate.tanks.through.objects.filter(
                    raidtemplate_id=OuterRef('id'),
                ).values('raidtemplate_id').annotate(
                    count=Count('id'),
                ).order_by().values('count'),
            ),
            count_damage_dealers=Subquery(
                RaidTemplate.damage_dealers.through.objects.filter(
                    raidtemplate_id=OuterRef('id'),
                ).values('raidtemplate_id').annotate(
                    count=Count('id'),
                ).order_by().values('count'),
            ),
            count_healers=Subquery(
                RaidTemplate.healers.through.objects.filter(
                    raidtemplate_id=OuterRef('id'),
                ).values('raidtemplate_id').annotate(
                    count=Count('id'),
                ).order_by().values('count'),
            ),
        ).annotate(
            ppl_total=(
                Coalesce(F('count_tanks'), 0)
                + Coalesce(F('count_damage_dealers'), 0)
                + Coalesce(F('count_healers'), 0)
            ),
        ).order_by('name')
        return qs.filter(is_base_template=True)


class AddToStaticForm(forms.Form):
    character_id = forms.ModelChoiceField(queryset=Character.objects.all(), label='')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super().__init__(*args, **kwargs)
        self.fields['character_id'].queryset = Character.objects.filter(
            user=self.request.user,
        )


class EditStaticView(DetailView):
    template_name = 'extra_ep/raids/static_detail.html'
    model = RaidTemplate

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        ppl_total = self.object.tanks.count() + self.object.healers.count() + self.object.damage_dealers.count()
        is_static_full = ppl_total >= self.object.max_total
        can_join = not is_static_full and not self.request.user.is_anonymous

        context['is_static_full'] = is_static_full

        context['tanks_table'] = self._make_context_table(self.object.tanks.all())
        context['can_add_tanks'] = can_join and (self.object.tanks.count() < self.object.max_tanks)

        context['healers_table'] = self._make_context_table(self.object.healers.all())
        context['can_add_healers'] = can_join and (
            self.object.healers.count() < self.object.max_healers
        )

        context['dd_table'] = self._make_context_table(self.object.damage_dealers.all())
        context['can_add_dd'] = can_join and (
            self.object.damage_dealers.count() < self.object.max_damage_dealers
        )

        context['add_to_static_form'] = can_join and AddToStaticForm(request=self.request)
        return context

    @staticmethod
    def _make_context_table(qs):
        data = list(qs.order_by('name'))  # todo order by class
        result = []
        for i in range((len(data) // 5) + 1):
            result.append(data[i * 5:(i + 1) * 5])

        return zip_longest(*result)


class Roles:
    ROLE_TANK = 'tank'
    ROLE_DD = 'dd'
    ROLE_HEAL = 'heal'


class AddToStaticView(FormView):
    form_class = AddToStaticForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def form_valid(self, form):
        template = get_object_or_404(RaidTemplate, id=self.kwargs['pk'])

        if Roles.ROLE_TANK in form.data:
            template.tanks.add(form.cleaned_data['character_id'])
        elif Roles.ROLE_HEAL in form.data:
            template.healers.add(form.cleaned_data['character_id'])
        else:
            template.damage_dealers.add(form.cleaned_data['character_id'])

        return super().form_valid(form)

    def get_success_url(self):
        return reverse('extra_ep:edit_static', kwargs={'pk': self.kwargs['pk']})
