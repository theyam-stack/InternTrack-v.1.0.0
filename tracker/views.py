import csv
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import HttpResponse
from django.db.models import Q
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .models import Internship, Company, Interview
from .forms import InternshipForm, CompanyForm, InterviewForm




# ---------- Internship list (Dev 1's view + your search/filter logic merged in) ----------

@login_required
def internship_list(request):
    internships = Internship.objects.filter(user=request.user)

    search_query = request.GET.get('q', '').strip()
    if search_query:
        internships = internships.filter(
            Q(role__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )

    status_filter = request.GET.get('status', '')
    if status_filter:
        internships = internships.filter(status=status_filter)

    sort_order = request.GET.get('sort', '-application_date')
    internships = internships.order_by(sort_order)

    context = {
        'internships': internships,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Internship.STATUS_CHOICES,
    }
    return render(request, 'tracker/internship_list.html', context)


# ---------- Dev 1's CRUD views ----------

@login_required
def internship_create(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            company_name = form.cleaned_data['company_name'].strip()
            company, created = Company.objects.get_or_create(name=company_name)

            internship = form.save(commit=False)
            internship.company = company
            internship.user = request.user
            internship.save()

            if internship.status == 'Interview' and request.POST.get('interview_date'):
                Interview.objects.create(
                    internship=internship,
                    interview_date=request.POST.get('interview_date'),
                    interview_type=request.POST.get('interview_type', ''),
                )

            return redirect('internship_list')
    else:
        form = InternshipForm()

    companies = Company.objects.all().order_by('name')
    return render(request, 'tracker/internship_form.html', {'form': form, 'companies': companies})


@login_required
def internship_update(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            company_name = form.cleaned_data['company_name'].strip()
            company, created = Company.objects.get_or_create(name=company_name)

            internship = form.save(commit=False)
            internship.company = company
            internship.save()

            if internship.status == 'Interview' and request.POST.get('interview_date'):
                Interview.objects.update_or_create(
                    internship=internship,
                    defaults={
                        'interview_date': request.POST.get('interview_date'),
                        'interview_type': request.POST.get('interview_type', ''),
                    }
                )

            return redirect('internship_list')
    else:
        form = InternshipForm(instance=internship)

    companies = Company.objects.all().order_by('name')
    interview_date_value = ''
    interview_type_value = ''
    existing_interview = internship.interviews.first()
    if existing_interview:
        interview_date_value = existing_interview.interview_date.strftime('%Y-%m-%dT%H:%M')
        interview_type_value = existing_interview.interview_type

    return render(request, 'tracker/internship_form.html', {
        'form': form,
        'companies': companies,
        'interview_date_value': interview_date_value,
        'interview_type_value': interview_type_value,
    })

@login_required
def internship_delete(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        internship.delete()
        return redirect('internship_list')
    return render(request, 'tracker/internship_confirm_delete.html', {'internship': internship})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # auto-login after registration
            return redirect('internship_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# ---------- Your dashboard/export views ----------

def clean_filename(name, default):
    name = name.strip() if name else default
    name = re.sub(r'[^a-zA-Z0-9_\-]', '_', name)
    return name or default


@login_required
def dashboard(request):
    internships = Internship.objects.filter(user=request.user)

    stats = {
        'total': internships.count(),
        'applied': internships.filter(status='Applied').count(),
        'interview': internships.filter(status='Interview').count(),
        'accepted': internships.filter(status='Accepted').count(),
        'rejected': internships.filter(status='Rejected').count(),
        'waiting': internships.filter(status='Waiting').count(),
    }

    context = {
        'stats': stats,
        'recent_internships': internships.order_by('-application_date')[:5],
    }
    return render(request, 'tracker/dashboard.html', context)


@login_required
def export_page(request):
    return render(request, 'tracker/export.html')


@login_required
def export_csv(request):
    internships = Internship.objects.filter(user=request.user).order_by('-application_date')

    filename = clean_filename(request.GET.get('filename'), 'internship_applications')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

    writer = csv.writer(response)
    writer.writerow(['Company', 'Role', 'Status', 'Application Date', 'Notes'])

    for item in internships:
        writer.writerow([
            item.company.name,
            item.role,
            item.get_status_display(),
            item.application_date,
            item.notes,
        ])

    return response


@login_required
def export_pdf(request):
    internships = Internship.objects.filter(user=request.user).order_by('-application_date')

    filename = clean_filename(request.GET.get('filename'), 'internship_report')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = [Paragraph("Internship Application Report", styles['Title'])]

    data = [['Company', 'Role', 'Status', 'Application Date']]
    for item in internships:
        data.append([item.company.name, item.role, item.get_status_display(), str(item.application_date)])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(table)

    doc.build(elements)
    return response

@login_required
def interview_create(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        form = InterviewForm(request.POST)
        if form.is_valid():
            interview = form.save(commit=False)
            interview.internship = internship
            interview.save()
            return redirect('internship_list')
    else:
        form = InterviewForm()
    return render(request, 'tracker/interview_form.html', {'form': form, 'internship': internship})

