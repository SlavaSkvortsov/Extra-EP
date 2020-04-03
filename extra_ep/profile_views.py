from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, FormView, UpdateView

from extra_ep.models import Character


class AddCharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        if kwargs.get('data', {}).get('name'):
            kwargs['instance'] = Character.objects.filter(name=kwargs['data']['name']).first()
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.instance is not None and self.instance.user and self.instance.user != self.request.user:
            raise ValidationError(
                'Этот персонаж уже принадлежит другому пользователю. '
                'Если это точно ваш персонаж - напишите Енотоводу!',
            )
        return name

    def save(self, commit=True):
        self.instance.user = self.request.user
        if commit:
            self.instance.save()

        return self.instance


class DeattachCharacterView(DeleteView):
    model = Character
    success_url = reverse_lazy('extra_ep:profile')
    template_name = 'extra_ep/profile/deattach_character.html'

    def get_object(self, queryset=None) -> Character:
        return get_object_or_404(Character, id=self.kwargs.get('character_id'))

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.user != request.user:
            raise Http404

        self.object.user = None
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())


class SetClassView(UpdateView):
    model = Character
    success_url = reverse_lazy('extra_ep:profile')


class ProfileView(FormView):
    form_class = AddCharacterForm
    template_name = 'extra_ep/profile/profile.html'
    success_url = reverse_lazy('extra_ep:profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['characters'] = Character.objects.filter(user=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
