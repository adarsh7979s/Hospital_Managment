import logging
import threading
import requests
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from django.conf import settings
from django.utils import timezone
from django.http import HttpResponseForbidden

from core.models import UserProfile, GoogleCredentials, AvailabilitySlot, Booking

logger = logging.getLogger(__name__)

# ==========================================
# Helpers
# ==========================================

def send_email_api_call(payload):
    try:
        print(f"[EMAIL API] Sending POST to {settings.EMAIL_SERVICE_URL} with payload: {payload}")
        response = requests.post(settings.EMAIL_SERVICE_URL, json=payload, timeout=5)
        print(f"[EMAIL API] Response: {response.status_code} - {response.text}")
        logger.info(f"Email service responded: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[EMAIL API] ERROR: Failed to call email service: {e}")
        logger.error(f"Failed to call email service: {e}")

def trigger_email_notification(trigger, email, **kwargs):
    print(f"\n[NOTIFICATION] Triggering email '{trigger}' to: {email}")
    payload = {
        "trigger": trigger,
        "email": email,
        **kwargs
    }
    threading.Thread(target=send_email_api_call, args=(payload,), daemon=True).start()


def create_google_calendar_event(user, title, start_time, end_time, description=""):
    try:
        creds_model = getattr(user, 'google_creds', None)
        if not creds_model:
            logger.info(f"User {user.username} has not connected Google Calendar.")
            return None
        
        credentials = creds_model.to_oauth_credentials()
        if credentials.expired and credentials.refresh_token:
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            creds_model.update_from_oauth_credentials(credentials)

        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=credentials)
        event_body = {
            'summary': title,
            'description': description,
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return event.get('id')
    except Exception as e:
        logger.error(f"Failed to create Google Calendar event for {user.username}: {e}")
        return None

def process_booking_background(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        slot = booking.slot
        patient = booking.patient
        doctor = slot.doctor

        # 1. Create on Patient's calendar
        patient_title = f"Appointment with Dr. {doctor.get_full_name() or doctor.username}"
        event_id_patient = create_google_calendar_event(patient, patient_title, slot.start_time, slot.end_time)
        if event_id_patient:
            booking.google_event_id_patient = event_id_patient

        # 2. Create on Doctor's calendar
        doctor_title = f"Appointment with {patient.get_full_name() or patient.username}"
        event_id_doctor = create_google_calendar_event(doctor, doctor_title, slot.start_time, slot.end_time)
        if event_id_doctor:
            booking.google_event_id_doctor = event_id_doctor

        booking.save()

        # 3. Trigger email confirmations
        # To Patient
        trigger_email_notification(
            trigger="BOOKING_CONFIRMATION",
            email=patient.email,
            recipient_name=patient.get_full_name() or patient.username,
            partner_name=doctor.get_full_name() or doctor.username,
            role="patient",
            start_time=slot.start_time.strftime('%Y-%m-%d %H:%M UTC')
        )
        # To Doctor
        trigger_email_notification(
            trigger="BOOKING_CONFIRMATION",
            email=doctor.email,
            recipient_name=doctor.get_full_name() or doctor.username,
            partner_name=patient.get_full_name() or patient.username,
            role="doctor",
            start_time=slot.start_time.strftime('%Y-%m-%d %H:%M UTC')
        )
    except Exception as e:
        logger.error(f"Error in background booking processing: {e}")

# ==========================================
# Authentication Views
# ==========================================

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role')

        if not username or not email or not password or not role:
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'core/signup.html')

        if role not in ['doctor', 'patient']:
            messages.error(request, "Invalid role selected.")
            return render(request, 'core/signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'core/signup.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return render(request, 'core/signup.html')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserProfile.objects.create(user=user, role=role)
        print(f"\n[SIGNUP] User successfully registered: {user.username} as {role} (Email: {user.email})")
        
        # Log the user in
        login(request, user)

        # Trigger welcome email in background
        trigger_email_notification(
            trigger="SIGNUP_WELCOME",
            email=user.email,
            name=user.get_full_name() or user.username
        )

        messages.success(request, f"Registration successful. Welcome, {user.username}!")
        return redirect('dashboard')

    return render(request, 'core/signup.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Logged in successfully. Welcome back, {user.username}!")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'core/login.html')


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# ==========================================
# Dashboard Routing
# ==========================================

@login_required
def dashboard_redirect_view(request):
    try:
        role = request.user.profile.role
        if role == 'doctor':
            return redirect('doctor_dashboard')
        elif role == 'patient':
            return redirect('patient_dashboard')
    except UserProfile.DoesNotExist:
        if request.user.is_superuser or request.user.is_staff:
            return redirect('/admin/')
        return HttpResponseForbidden("User profile not found. Please contact the administrator.")
    
    return HttpResponseForbidden("Unauthorized role.")


# ==========================================
# Doctor Space
# ==========================================

@login_required
def doctor_dashboard(request):
    if request.user.profile.role != 'doctor':
        return HttpResponseForbidden("Only doctors can access this dashboard.")

    slots = AvailabilitySlot.objects.filter(doctor=request.user).order_by('start_time')
    # Filter bookings where slot doctor is request.user
    bookings = Booking.objects.filter(slot__doctor=request.user).order_by('slot__start_time')
    
    # Check calendar connection
    calendar_connected = GoogleCredentials.objects.filter(user=request.user).exists()
    
    google_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    return render(request, 'core/doctor_dashboard.html', {
        'slots': slots,
        'bookings': bookings,
        'calendar_connected': calendar_connected,
        'google_configured': google_configured
    })


@login_required
def add_availability(request):
    if request.user.profile.role != 'doctor':
        return HttpResponseForbidden("Only doctors can add availability.")

    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        if not date_str or not start_time_str or not end_time_str:
            messages.error(request, "Please fill in date, start time, and end time.")
            return redirect('doctor_dashboard')

        try:
            start_dt = timezone.make_aware(datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M"))
            end_dt = timezone.make_aware(datetime.strptime(f"{date_str} {end_time_str}", "%Y-%m-%d %H:%M"))
        except ValueError:
            messages.error(request, "Invalid date or time format.")
            return redirect('doctor_dashboard')

        if start_dt <= timezone.now():
            messages.error(request, "Availability slots must be in the future.")
            return redirect('doctor_dashboard')

        if end_dt <= start_dt:
            messages.error(request, "End time must be after start time.")
            return redirect('doctor_dashboard')

        # Check overlapping slots for this doctor
        overlap = AvailabilitySlot.objects.filter(
            doctor=request.user,
            start_time__lt=end_dt,
            end_time__gt=start_dt
        ).exists()

        if overlap:
            messages.error(request, "This slot overlaps with an existing availability slot.")
            return redirect('doctor_dashboard')

        AvailabilitySlot.objects.create(
            doctor=request.user,
            start_time=start_dt,
            end_time=end_dt
        )
        messages.success(request, "Availability slot created successfully.")
    
    return redirect('doctor_dashboard')


# ==========================================
# Patient Space
# ==========================================

@login_required
def patient_dashboard(request):
    if request.user.profile.role != 'patient':
        return HttpResponseForbidden("Only patients can access this dashboard.")

    # Get list of doctors
    doctors = User.objects.filter(profile__role='doctor')
    
    # Selected doctor
    selected_doctor_id = request.GET.get('doctor_id')
    selected_doctor = None
    available_slots = []
    
    if selected_doctor_id:
        try:
            selected_doctor = User.objects.get(id=selected_doctor_id, profile__role='doctor')
            # Available slots = in the future and not booked
            available_slots = AvailabilitySlot.objects.filter(
                doctor=selected_doctor,
                start_time__gt=timezone.now(),
                is_booked=False
            ).order_by('start_time')
        except User.DoesNotExist:
            messages.error(request, "Selected doctor does not exist.")

    # Patient's bookings
    my_bookings = Booking.objects.filter(patient=request.user).order_by('slot__start_time')

    # Calendar connection status
    calendar_connected = GoogleCredentials.objects.filter(user=request.user).exists()
    google_configured = bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET)

    return render(request, 'core/patient_dashboard.html', {
        'doctors': doctors,
        'selected_doctor': selected_doctor,
        'slots': available_slots,
        'bookings': my_bookings,
        'calendar_connected': calendar_connected,
        'google_configured': google_configured
    })


@login_required
def book_appointment(request):
    if request.user.profile.role != 'patient':
        return HttpResponseForbidden("Only patients can book appointments.")

    if request.method == 'POST':
        slot_id = request.POST.get('slot_id')
        if not slot_id:
            messages.error(request, "Invalid slot selected.")
            return redirect('patient_dashboard')

        # Handle race condition using select_for_update
        try:
            with transaction.atomic():
                # Lock the slot row in the DB during verification and booking creation
                slot = AvailabilitySlot.objects.select_for_update().get(id=slot_id)
                
                # Check if slot is in the past
                if slot.start_time <= timezone.now():
                    messages.error(request, "Cannot book a slot in the past.")
                    return redirect('patient_dashboard')

                if slot.is_booked:
                    messages.error(request, "This slot has already been booked by another patient.")
                    return redirect('patient_dashboard')

                # Create the booking
                booking = Booking.objects.create(
                    patient=request.user,
                    slot=slot
                )

                # Mark the slot as booked
                slot.is_booked = True
                slot.save()
                print(f"\n[BOOKING] Slot booked: Patient '{request.user.username}' with Doctor '{slot.doctor.username}' for slot ID: {slot.id} ({slot.start_time})")

            # The transaction has successfully committed and locked row released.
            # Perform post-processing (Google Calendar integration & email triggers) in a background thread
            threading.Thread(target=process_booking_background, args=(booking.id,), daemon=True).start()

            messages.success(request, f"Appointment booked successfully with Dr. {slot.doctor.get_full_name() or slot.doctor.username}!")
            return redirect('patient_dashboard')

        except AvailabilitySlot.DoesNotExist:
            messages.error(request, "Availability slot not found.")
        except Exception as e:
            logger.error(f"Error booking appointment: {e}")
            messages.error(request, "An error occurred during booking. Please try again.")

    return redirect('patient_dashboard')


# ==========================================
# Google OAuth Flow
# ==========================================

from google_auth_oauthlib.flow import Flow

def get_google_oauth_flow(request):
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    # We request the calendar scope, offline access, and consent prompt to ensure we get a refresh token
    flow = Flow.from_client_config(
        client_config,
        scopes=['https://www.googleapis.com/auth/calendar.events'],
        redirect_uri=settings.GOOGLE_REDIRECT_URI
    )
    return flow


@login_required
def google_auth_redirect(request):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        messages.error(request, "Google Calendar integration is not configured on the server. Client ID and Secret are missing.")
        return redirect('dashboard')

    flow = get_google_oauth_flow(request)
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )
    request.session['oauth_state'] = state
    return redirect(authorization_url)


@login_required
def google_auth_callback(request):
    if 'oauth_state' not in request.session:
        messages.error(request, "OAuth state missing. Session expired.")
        return redirect('dashboard')

    state = request.session['oauth_state']
    flow = get_google_oauth_flow(request)
    # Reconstruct state
    flow.fetch_token(authorization_response=request.build_absolute_uri(), state=state)

    credentials = flow.credentials

    # Save to database
    # Overwrite if exists, otherwise create
    google_creds, created = GoogleCredentials.objects.get_or_create(
        user=request.user,
        defaults={
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'scopes': ','.join(credentials.scopes),
            'expiry': timezone.make_aware(credentials.expiry)
        }
    )

    if not created:
        google_creds.access_token = credentials.token
        if credentials.refresh_token:
            google_creds.refresh_token = credentials.refresh_token
        google_creds.expiry = timezone.make_aware(credentials.expiry)
        google_creds.save()

    messages.success(request, "Successfully connected Google Calendar!")
    return redirect('dashboard')
