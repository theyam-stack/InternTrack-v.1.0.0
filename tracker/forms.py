from django import forms
from .models import Internship, Company, Interview


class InternshipForm(forms.ModelForm):
    company_name = forms.CharField(max_length=200, label='Company')

    class Meta:
        model = Internship
        fields = ['company_name', 'role', 'status', 'application_date', 'notes']
        widgets = {
            'application_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.company:
            self.fields['company_name'].initial = self.instance.company.name


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'location', 'website']


class InterviewForm(forms.ModelForm):
    class Meta:
        model = Interview
        fields = ['interview_date', 'interview_type', 'notes']
        widgets = {
            'interview_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }