from django.db import models
from django.utils import timezone


class Incident(models.Model):
    PRIORITY_LOW = 'low'
    PRIORITY_MEDIUM = 'medium'
    PRIORITY_HIGH = 'high'
    PRIORITY_CRITICAL = 'critical'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
        (PRIORITY_CRITICAL, 'Critical'),
    ]

    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    # SLA settings (in hours)
    SLA_CRITICAL = 4
    SLA_HIGH = 8
    SLA_MEDIUM = 24
    SLA_LOW = 72

    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default=PRIORITY_MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    assigned_engineer = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolution_notes = models.TextField(blank=True, null=True)
    sla_deadline = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Set SLA deadline on creation based on priority
        if not self.pk and not self.sla_deadline:
            sla_hours = self.get_sla_hours()
            if sla_hours:
                from datetime import timedelta
                self.sla_deadline = timezone.now() + timedelta(hours=sla_hours)
        super().save(*args, **kwargs)

    def get_sla_hours(self):
        mapping = {
            self.PRIORITY_CRITICAL: self.SLA_CRITICAL,
            self.PRIORITY_HIGH: self.SLA_HIGH,
            self.PRIORITY_MEDIUM: self.SLA_MEDIUM,
            self.PRIORITY_LOW: self.SLA_LOW,
        }
        return mapping.get(self.priority)

    @property
    def incident_id(self):
        return f"INC-{self.pk:06d}"

    @property
    def status_class(self):
        mapping = {
            self.STATUS_OPEN: 'open',
            self.STATUS_IN_PROGRESS: 'in-progress',
            self.STATUS_RESOLVED: 'resolved',
            self.STATUS_CLOSED: 'closed',
        }
        return mapping.get(self.status, 'open')

    @property
    def priority_class(self):
        mapping = {
            self.PRIORITY_LOW: 'low',
            self.PRIORITY_MEDIUM: 'medium',
            self.PRIORITY_HIGH: 'high',
            self.PRIORITY_CRITICAL: 'critical',
        }
        return mapping.get(self.priority, 'medium')

    @property
    def sla_status(self):
        if not self.sla_deadline:
            return 'unknown'
        if self.status in [self.STATUS_RESOLVED, self.STATUS_CLOSED]:
            return 'resolved'
        if timezone.now() > self.sla_deadline:
            return 'breached'
        return 'within_sla'

    @property
    def sla_status_display(self):
        mapping = {
            'within_sla': 'Within SLA',
            'breached': 'SLA Breached',
            'resolved': 'Resolved',
            'unknown': 'Unknown',
        }
        return mapping.get(self.sla_status, 'Unknown')

    @property
    def sla_status_class(self):
        mapping = {
            'within_sla': 'success',
            'breached': 'danger',
            'resolved': 'secondary',
            'unknown': 'secondary',
        }
        return mapping.get(self.sla_status, 'secondary')


class IncidentHistory(models.Model):
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
        ('priority_changed', 'Priority Changed'),
        ('assigned', 'Assigned'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, related_name='history')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField(blank=True, null=True)
    changed_by = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.incident.incident_id} - {self.get_action_display()}"
