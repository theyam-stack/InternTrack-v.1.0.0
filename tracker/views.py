from django.shortcuts import render, redirect, get_object_or_404
from .models import Internship
from .forms import InternshipForm

def internship_list(request):
    internships = Internship.objects.all()
    return render(request, 'tracker/internship_list.html', {'internships': internships})

def internship_create(request):
    if request.method == 'POST':
        form = InternshipForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('internship_list')
    else:
        form = InternshipForm()
    return render(request, 'tracker/internship_form.html', {'form': form})

def internship_update(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        form = InternshipForm(request.POST, instance=internship)
        if form.is_valid():
            form.save()
            return redirect('internship_list')
    else:
        form = InternshipForm(instance=internship)
    return render(request, 'tracker/internship_form.html', {'form': form})

def internship_delete(request, pk):
    internship = get_object_or_404(Internship, pk=pk)
    if request.method == 'POST':
        internship.delete()
        return redirect('internship_list')
    return render(request, 'tracker/internship_confirm_delete.html', {'internship': internship})