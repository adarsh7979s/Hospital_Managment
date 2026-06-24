# Video Demo Script - Mini Hospital Management System (HMS)

This script is designed to help you record your **10-minute screen recording** demonstrating all features and code structure. 

Before starting, run `python scratch/seed_demo.py` in your terminal (already run for you!) to ensure the database is populated with clean demo accounts.

---

## ⏱️ Video Timeline Overview
1. **0:00 - 1:00**: Project Overview & Tech Stack Intro
2. **1:00 - 2:30**: Doctor Flow (Sign Up, Login, and Slot Creation)
3. **2:30 - 4:30**: Patient Flow (Sign Up, Doctor Selection, and Slot Booking)
4. **4:30 - 5:30**: Slot Blocking & Race Condition Verification
5. **5:30 - 7:00**: Email Notifications (Serverless Trigger & Mock SMTP Output)
6. **7:00 - 8:30**: Google Calendar OAuth Integration Explanation
7. **8:30 - 10:00**: Code Walkthrough & Design Decision Defense

---

## 🎙️ Script & Action Guide

### Section 1: Project Overview & Tech Stack (0:00 - 1:00)
* **What to show on screen**: Open the home page of the application (`http://127.0.0.1:8000/`) showing the clean, clinical teal/sky-blue login card with the floating AI Assistant in the bottom right corner.
* **What to say**:
  > "Hello, my name is [Your Name], and this is a demonstration of my Mini Hospital Management System built for the Python Serverless Backend Track. 
  > The system is fully runnable locally and composed of a Django web application, a Serverless Framework email notification service running via serverless-offline, and a local mock SMTP server to catch outbound email payloads.
  > As you can see, the UI is styled with a premium glassmorphic clinical theme, and includes an interactive client-side AI Care Assistant to help guide patients and doctors."

---

### Section 2: Doctor Flow (1:00 - 2:30)
* **What to show on screen**: 
  1. Click **Sign Up**, choose **Doctor** role, and register a new doctor user (e.g. `dr_test`, `dr_test@example.com`).
  2. Click **Login** and log in with the pre-seeded credentials:
     * **Username**: `dr_smith`
     * **Password**: `password123`
  3. On the **Doctor Dashboard**, create a new availability slot for **tomorrow** (e.g., from `15:00` to `16:00`). Show that it gets added to the "My Availability Slots" list.
* **What to say**:
  > "Let's begin by demonstrating the Doctor's flow. I can sign up a new doctor user easily. For this demo, let's log in to our pre-seeded doctor account, `dr_smith`.
  > On the Doctor Dashboard, doctors can manage their availability slots. Let's add a new slot for tomorrow from 3:00 PM to 4:00 PM. 
  > When I click 'Add Slot', the slot is created and instantly appears in my availability list. Doctors can only see and manage their own availability slots and bookings, guaranteeing role-based data isolation."

---

### Section 3: Patient Flow (2:30 - 4:30)
* **What to show on screen**:
  1. Log out of the doctor dashboard.
  2. Click **Login** and log in with the pre-seeded patient account:
     * **Username**: `patient_alice`
     * **Password**: `password123`
  3. On the **Patient Dashboard**, select **Dr. John Smith** from the doctor dropdown.
  4. Select the `10:00 - 11:00` slot and click **Book Appointment**. Show the success message and that the booking now appears under **My Scheduled Appointments**.
* **What to say**:
  > "Now, let's switch to the Patient's perspective. I will log in as `patient_alice`.
  > On the Patient Dashboard, patients can view all available doctors in the hospital. If I select `Dr. John Smith`, the system dynamically queries and displays his future, unbooked availability slots.
  > Let's select the 10:00 AM slot and click 'Book Appointment'. 
  > The appointment is booked instantly, and is added to my 'Scheduled Appointments' list with full details."

---

### Section 4: Slot Blocking & Race Condition Verification (4:30 - 5:30)
* **What to show on screen**:
  1. Log out of Alice's account.
  2. Log in as the second patient:
     * **Username**: `patient_bob`
     * **Password**: `password123`
  3. Select **Dr. John Smith** from the dropdown. 
  4. Point out that the `10:00 - 11:00` slot booked by Alice is **no longer visible** to Bob. Only the remaining slots (`11:00` and `14:00`) are shown.
* **What to say**:
  > "To verify that slot blocking works, I will log out of Alice's account and log in as `patient_bob`.
  > When I select Dr. John Smith, notice that the 10:00 AM slot Alice just booked is no longer visible to Bob. It has been successfully blocked from other patients.
  > The backend handles concurrent race conditions using database-level locking transactions. If two patients attempt to book the exact same slot at the exact same split-second, Django's row-locking blocks the second transaction, preventing double bookings."

---

### Section 5: Email Notifications (5:30 - 7:00)
* **What to show on screen**: 
  1. Open your terminal window where the unbuffered Mock SMTP Server is running (`python -u scratch/smtp_server.py`).
  2. Scroll up to show the logged outputs:
     * The `SIGNUP_WELCOME` mail content logged when `dr_test` registered.
     * The `BOOKING_CONFIRMATION` mail content logged when `patient_alice` booked Dr. Smith.
* **What to say**:
  > "Let's check the serverless email triggers. The Django backend connects to a Serverless Framework email service running locally via serverless-offline.
  > As we can see in our local SMTP console log, the serverless service successfully catches outbound emails.
  > Here is the welcome email payload sent via the `SIGNUP_WELCOME` trigger when we registered the new doctor.
  > And here is the confirmation email sent via the `BOOKING_CONFIRMATION` trigger containing the specific doctor, patient, and time details."

---

### Section 6: Google Calendar OAuth Integration (7:00 - 8:30)
* **What to show on screen**:
  1. Navigate back to the web browser. Show the Google Calendar integration status dot (currently red/disconnected).
  2. Click **Connect Google Calendar** to trigger the Google OAuth login page (if configured, or explain the redirection flow to the evaluator).
* **What to say**:
  > "For Google Calendar synchronization, both the doctor and patient dashboards include a 'Connect Google Calendar' button.
  > Clicking this triggers the Google OAuth2 flow using the `google-auth-oauthlib` package, requesting permission to write calendar events.
  > Once authorized, OAuth tokens are securely stored in the database. When an appointment is booked, a background daemon thread in Django automatically refreshes the tokens if expired, and inserts a calendar event with a customized title onto both the doctor's and patient's Google Calendar."

---

### Section 7: Code Walkthrough & Design Decision Defense (8:30 - 10:00)
* **What to show on screen**: Open VS Code / IDE.
  1. Open [views.py](file:///c:/Users/91797/OneDrive/Desktop/Projects/Hospital_Managment/hms/core/views.py) and scroll to `book_appointment` (around line 348). Show the `with transaction.atomic():` and `select_for_update()` block.
  2. Open [handler.py](file:///c:/Users/91797/OneDrive/Desktop/Projects/Hospital_Managment/email-service/handler.py) in the `email-service` directory.
* **What to say**:
  > "Let's review the code structure. In `hms/core/views.py`, under the booking endpoint, we wrap the verification and reservation in a database transaction using `transaction.atomic()`, and lock the row using `select_for_update()`.
  > This is our primary design decision: database row-level locking vs. application-level checks. 
  > While application-level checks are simpler to implement, they fail under high concurrency and horizontal scaling because web workers don't share memory. Database-level row locking is the only bulletproof way to prevent race conditions and guarantee scheduling consistency in a production-grade healthcare application.
  > In the `email-service` folder, `serverless.yml` and `handler.py` define the serverless triggers, decoupling the notification service from the main web application.
  > That completes my demonstration. Thank you for your time!"

---

## 💡 Quick Tips for Recording
* **Resolution**: Record at a standard 1080p resolution so code and text are sharp and readable.
* **Audio**: Use a headset microphone in a quiet room to ensure clear audio.
* **Run a Trial**: Do a quick 1-minute dry-run to ensure your voice is captured alongside the screen.
* **Code Size**: In VS Code, increase your font size slightly (`Ctrl` + `+`) so it is readable on video.
