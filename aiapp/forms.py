# aiapp/forms.py

from django import forms

class UploadForm(forms.Form):
    query = forms.CharField(required=False, label='', widget=forms.TextInput(attrs={
        'placeholder': 'Search text or upload file...',
        'class': 'flex-1 px-4 py-2 rounded-lg shadow border border-gray-300'
    }))
    image = forms.ImageField(required=False)
    audio = forms.FileField(required=False)
