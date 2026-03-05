from django import forms
from .models import Monitor, Alert

class MonitorForm(forms.ModelForm):

    class Meta:
        model = Monitor
        fields = [
            'name', 'url', 'check_type', 'keyword', 'check_interval', 'timeout',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'mdc-text-field__input',
                'placeholder': 'e.g., My Website',
            }),
            'url': forms.URLInput(attrs={
                'class': 'mdc-text-field__input',
                'placeholder': 'https://example.com',
            }),
            'check_type': forms.Select(attrs={'class': 'mdc-select__native-control'}),
            'keyword': forms.TextInput(attrs={
                'class': 'mdc-text-field__input',
                'placeholder': 'Optional: keyword to search for',
            }),
            'check_interval': forms.NumberInput(attrs={
                'class': 'mdc-text-field__input',
                'min': '30',
                'max': '3600',
            }),
            'timeout': forms.NumberInput(attrs={
                'class': 'mdc-text-field__input',
                'min': '5',
                'max': '120',
            }),
        }
        help_texts = {
            'check_interval': 'Check interval in seconds (30-3600)',
            'timeout': 'Request timeout in seconds (5-120)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name != 'check_type':
                field.widget.attrs.update({'class': 'mdc-text-field__input'})

class AlertForm(forms.ModelForm):

    class Meta:
        model = Alert
        fields = ['alert_type', 'target', 'is_enabled']
        widgets = {
            'alert_type': forms.Select(attrs={'class': 'mdc-select__native-control'}),
            'target': forms.TextInput(attrs={
                'class': 'mdc-text-field__input',
                'placeholder': 'email@example.com or Telegram chat ID',
            }),
            'is_enabled': forms.CheckboxInput(attrs={'class': 'mdc-checkbox__native-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['target'].label = 'Email or Telegram Chat ID'
