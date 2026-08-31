from django.contrib import admin
from .models import Company, Internship, Interview

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'website')
    search_fields = ('name',)


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    list_display = ('role', 'company', 'user', 'status', 'application_date')
    list_filter = ('status',)
    search_fields = ('role', 'company__name')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('internship', 'interview_date', 'interview_type')
    list_filter = ('interview_type',)