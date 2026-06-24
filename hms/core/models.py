from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Patient'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class GoogleCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_creds')
    access_token = models.TextField()
    refresh_token = models.TextField(null=True, blank=True)
    token_uri = models.CharField(max_length=255, default="https://oauth2.googleapis.com/token")
    client_id = models.TextField()
    client_secret = models.TextField()
    scopes = models.TextField()
    expiry = models.DateTimeField()

    def to_oauth_credentials(self):
        """Converts database values into a Google Credentials object."""
        from google.oauth2.credentials import Credentials  # noqa: deferred import for linter compatibility
        # Convert expiry to naive/aware datetime as expected or string in ISO format
        # Under the hood google credentials expects a datetime or None.
        return Credentials(
            token=self.access_token,
            refresh_token=self.refresh_token,
            token_uri=self.token_uri,
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=self.scopes.split(','),
            expiry=self.expiry.replace(tzinfo=None) if self.expiry else None
        )

    def update_from_oauth_credentials(self, credentials):
        """Updates database record from a Google Credentials object."""
        self.access_token = credentials.token
        if credentials.refresh_token:
            self.refresh_token = credentials.refresh_token
        self.expiry = credentials.expiry
        self.save()

    def __str__(self):
        return f"Google Creds for {self.user.username}"


class AvailabilitySlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='availability_slots')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        ordering = ['start_time']

    def __str__(self):
        return f"{self.doctor.get_full_name() or self.doctor.username}: {self.start_time.strftime('%Y-%m-%d %H:%M')} - {self.end_time.strftime('%H:%M')}"


class Booking(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    slot = models.OneToOneField(AvailabilitySlot, on_delete=models.CASCADE, related_name='booking')
    google_event_id_patient = models.CharField(max_length=255, null=True, blank=True)
    google_event_id_doctor = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking: {self.patient.username} with {self.slot.doctor.username} on {self.slot.start_time.strftime('%Y-%m-%d %H:%M')}"
