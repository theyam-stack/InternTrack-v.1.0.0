from django.db import models

class Internship(models.Model):
    company_name = models.CharField(max_length=200)
    role = models.CharField(max_length=200)
    status_choices = [
        ('Pending', 'รอพิจารณา'),
        ('Interview', 'นัดสัมภาษณ์'),
        ('Accepted', 'ได้ที่ฝึกงาน'),
        ('Rejected', 'ไม่ผ่าน')
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Pending')
    application_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.company_name} - {self.role}"