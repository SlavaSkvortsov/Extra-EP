from django import forms

from extra_ep.models import Report


class UploadFile(forms.ModelForm):
    log_file = forms.FileField()

    class Meta:
        model = Report
        fields = ('static', 'log_file')

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        self.instance.uploaded_by = self.user
        return super().save(commit)


class ChangeExportedForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('flushed', )
        widgets = {'flushed': forms.HiddenInput()}

    def get_initial_for_field(self, field, field_name):
        if self.instance and field_name == 'flushed':
            return not self.instance.flushed

        return super().get_initial_for_field(field, field_name)
