from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Company(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Internship(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=200)

    STATUS_CHOICES = [
        ('Applied', 'Applied'),
        ('Interview', 'Interview'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
        ('Waiting', 'Waiting for response'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Applied')
    application_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.company.name} - {self.role}"

    def status_color(self):
        colors = {
            'Applied': 'blue',
            'Interview': 'orange',
            'Accepted': 'green',
            'Rejected': 'red',
            'Waiting': 'gray',
        }
        return colors.get(self.status, 'black')

    def days_since_applied(self):
        from datetime import date
        return (date.today() - self.application_date).days


class Interview(models.Model):
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateTimeField()
    interview_type = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)

    def days_until_interview(self):
        from datetime import datetime
        delta = self.interview_date.date() - datetime.now().date()
        return delta.days

    def interview_status_text(self):
        days = self.days_until_interview()
        if days > 0:
            return f"In {days} days"
        elif days == 0:
            return "Today"
        else:
            return f"{abs(days)} days ago"

    def __str__(self):
        return f"Interview for {self.internship} on {self.interview_date}"