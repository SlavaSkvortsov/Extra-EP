from django import forms


class UploadFile(forms.Form):
    url = forms.URLField()
