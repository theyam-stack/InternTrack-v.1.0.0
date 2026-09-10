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


from django.utils import timezone
from datetime import timedelta

@login_required
def internship_detail(request, pk):
    internship = get_object_or_404(Internship, pk=pk, user=request.user)

    stage_order = ['Applied', 'Interview', 'Accepted', 'Rejected', 'Waiting']
    stage_labels = {
        'Applied': ('Applied', 'Application submitted'),
        'Interview': ('Interview', 'Interview stage reached'),
        'Accepted': ('Accepted', 'Offer accepted'),
        'Rejected': ('Rejected', 'Application closed'),
        'Waiting': ('Waiting', 'Awaiting response'),
    }
    current_index = stage_order.index(internship.status) if internship.status in stage_order else 0
    timeline = []
    for i, key in enumerate(stage_order[:current_index + 1]):
        label, detail = stage_labels[key]
        timeline.append({
            'label': label,
            'detail': detail,
            'done': i < current_index,
            'current': i == current_index,
        })

    return render(request, 'tracker/internship_detail.html', {
        'internship': internship,
        'timeline': timeline,
    })


@login_required
def company_list(request):
    companies = Company.objects.filter(internship__user=request.user).distinct()

    stage_rank = {'Applied': 1, 'Waiting': 2, 'Interview': 3, 'Rejected': 4, 'Accepted': 5}
    company_data = []
    for company in companies:
        apps = Internship.objects.filter(company=company, user=request.user)
        furthest = max(apps, key=lambda a: stage_rank.get(a.status, 0), default=None)
        company.application_count = apps.count()
        company.furthest_stage = furthest.status if furthest else '—'
        company_data.append(company)

    return render(request, 'tracker/company_list.html', {'companies': company_data})


@login_required
def search(request):
    searched = bool(request.GET)
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    company_filter = request.GET.get('company', '')
    date_from = request.GET.get('from', '')
    date_to = request.GET.get('to', '')

    results = Internship.objects.filter(user=request.user)

    if search_query:
        results = results.filter(
            Q(role__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(company__location__icontains=search_query) |
            Q(notes__icontains=search_query)
        )
    if status_filter:
        results = results.filter(status=status_filter)
    if company_filter:
        results = results.filter(company__pk=company_filter)
    if date_from:
        results = results.filter(application_date__gte=date_from)
    if date_to:
        results = results.filter(application_date__lte=date_to)

    results = results.order_by('-application_date')

    return render(request, 'tracker/search.html', {
        'searched': searched,
        'search_query': search_query,
        'status_filter': status_filter,
        'company_filter': company_filter,
        'date_from': date_from,
        'date_to': date_to,
        'status_choices': Internship.STATUS_CHOICES,
        'companies': Company.objects.filter(internship__user=request.user).distinct(),
        'results': results,
        'total_count': results.count(),
    })


@login_required
def interview_list(request):
    range_filter = request.GET.get('range', '30')
    range_options = [('7', 'Next 7 days'), ('30', 'Next 30 days'), ('all', 'All upcoming')]

    now = timezone.now()
    base_qs = Interview.objects.filter(internship__user=request.user)

    upcoming = base_qs.filter(interview_date__gte=now)
    if range_filter != 'all':
        days = int(range_filter)
        upcoming = upcoming.filter(interview_date__lte=now + timedelta(days=days))
    upcoming = upcoming.order_by('interview_date')

    past = base_qs.filter(interview_date__lt=now).order_by('-interview_date')

    return render(request, 'tracker/interview_list.html', {
        'upcoming': upcoming,
        'past': past,
        'range_filter': range_filter,
        'range_options': range_options,
    })


@login_required
def settings_view(request):
    saved = False
    if request.method == 'POST':
        full_name = request.POST.get('display_name', '').strip()
        email = request.POST.get('email', '').strip()
        if full_name:
            parts = full_name.split(' ', 1)
            request.user.first_name = parts[0]
            request.user.last_name = parts[1] if len(parts) > 1 else ''
        request.user.email = email
        request.user.save()
        saved = True

    return render(request, 'tracker/settings.html', {'saved': saved})