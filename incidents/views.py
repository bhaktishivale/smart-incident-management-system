from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import IncidentForm
from .models import Incident


def home(request):
    return render(request, 'home.html')


class CustomLoginView(LoginView):
    template_name = 'login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = 'home'


@login_required
def dashboard(request):
    incidents = Incident.objects.all()

    # Calculate analytics data for charts
    open_count = incidents.filter(
        status__in=[Incident.STATUS_OPEN, Incident.STATUS_IN_PROGRESS]
    ).count()
    resolved_count = incidents.filter(
        status__in=[Incident.STATUS_RESOLVED, Incident.STATUS_CLOSED]
    ).count()

    priority_low = incidents.filter(priority=Incident.PRIORITY_LOW).count()
    priority_medium = incidents.filter(priority=Incident.PRIORITY_MEDIUM).count()
    priority_high = incidents.filter(priority=Incident.PRIORITY_HIGH).count()
    priority_critical = incidents.filter(priority=Incident.PRIORITY_CRITICAL).count()

    # Critical incidents for notifications
    critical_incidents = incidents.filter(
        priority=Incident.PRIORITY_CRITICAL,
        status__in=[Incident.STATUS_OPEN, Incident.STATUS_IN_PROGRESS]
    )[:5]

    context = {
        'stats': {
            'total': incidents.count(),
            'open': open_count,
            'resolved': resolved_count,
            'critical': priority_critical,
        },
        'recent_incidents': incidents[:5],
        'recent_activity': _build_recent_activity(incidents[:5]),
        'critical_incidents': critical_incidents,
        'chart_data': {
            'status_pie': {
                'labels': ['Open', 'Resolved'],
                'data': [open_count, resolved_count],
                'colors': ['#f59e0b', '#10b981'],
            },
            'priority_bar': {
                'labels': ['Low', 'Medium', 'High', 'Critical'],
                'data': [priority_low, priority_medium, priority_high, priority_critical],
                'colors': ['#64748b', '#f59e0b', '#ef4444', '#dc2626'],
            },
        },
    }
    return render(request, 'dashboard.html', context)


def _build_recent_activity(incidents):
    activity = []
    for incident in incidents:
        activity.append({
            'message': f'{incident.title} — {incident.get_status_display()}',
            'time': incident.created_date.strftime('%b %d, %Y %H:%M'),
            'icon': 'exclamation-circle' if incident.status == Incident.STATUS_OPEN else 'check-circle',
            'icon_class': 'red' if incident.priority == Incident.PRIORITY_CRITICAL else 'blue',
        })
    return activity


@login_required
def incident_list(request):
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    engineer_filter = request.GET.get('engineer', '').strip()

    incidents = Incident.objects.all()

    if query:
        incidents = incidents.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
        )

    if status_filter:
        incidents = incidents.filter(status=status_filter)

    if priority_filter:
        incidents = incidents.filter(priority=priority_filter)

    if engineer_filter:
        incidents = incidents.filter(assigned_engineer__icontains=engineer_filter)

    context = {
        'incidents': incidents,
        'query': query,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'engineer_filter': engineer_filter,
        'status_choices': Incident.STATUS_CHOICES,
        'priority_choices': Incident.PRIORITY_CHOICES,
    }

    return render(request, 'incident_list.html', context)


@login_required
def incident_create(request):
    if request.method == 'POST':
        form = IncidentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incident created successfully.')
            return redirect('incident_list')
    else:
        form = IncidentForm()

    return render(request, 'incident_form.html', {
        'form': form,
        'page_title': 'Add Incident',
        'submit_label': 'Create Incident',
    })


@login_required
def incident_update(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == 'POST':
        form = IncidentForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incident updated successfully.')
            return redirect('incident_list')
    else:
        form = IncidentForm(instance=incident)

    return render(request, 'incident_form.html', {
        'form': form,
        'incident': incident,
        'page_title': 'Edit Incident',
        'submit_label': 'Save Changes',
    })


@login_required
def incident_delete(request, pk):
    incident = get_object_or_404(Incident, pk=pk)

    if request.method == 'POST':
        incident.delete()
        messages.success(request, 'Incident deleted successfully.')
        return redirect('incident_list')

    return render(request, 'incident_confirm_delete.html', {
        'incident': incident,
    })
