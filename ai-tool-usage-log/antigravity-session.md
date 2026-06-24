# AI Tool Usage Log

This file contains the log of interactions with Antigravity, the AI coding assistant, used to build the Mini Hospital Management System.

## Session Information
- **AI Assistant**: Antigravity (powered by Gemini 3.5 Flash)
- **Task**: Shortlisting Task A — Mini Hospital Management System (HMS)
- **Date**: 2026-06-24

## Thread Summary

### Prompt 1: Initial Requirement Analysis
- **User Request**: Initial PDF attachment representing Task 1 Shortlisting Task instructions.
- **AI Action**: 
  - Analyzed requirements: Roles (Doctor/Patient), Core Auth, Availability management, Booking Flow, Google Calendar Integration with OAuth2, Serverless Email Service with `serverless-offline`.
  - Audited local system tools: Python 3.14.3, Node v24.13.0, npm 11.6.2. Checked Serverless Framework global install (installed Serverless CLI v4.38.1).
  - Authored standard `requirements.txt` listing Django and Google API packages.
  - Created `implementation_plan.md` to specify database choice (SQLite instead of global PostgreSQL to allow portable local execution), schema, OAuth flow details, race condition transaction locking, and verification.

### Prompt 2: Execution Start
- **User Request**: User automatic approval of the implementation plan.
- **AI Action**:
  - Initialized task checklist (`task.md`).
  - Created Django project `hms` and app `core`.
  - Implemented database models in `core/models.py`:
    - `UserProfile` (linked to standard User with `'doctor'` or `'patient'` roles).
    - `GoogleCredentials` (holds access token, refresh token, client ID/secret, expiry).
    - `AvailabilitySlot` (start/end times, doctor reference, booked status).
    - `Booking` (patient reference, slot reference, patient/doctor calendar event IDs).
  - Modified project `settings.py` to register the `core` app, load credentials from `.env` using `django-environ`, configure login/logout redirects, and set the default local Serverless offline email URL.
  - Applied migrations to database.
  - Implemented views in `core/views.py`:
    - Role-based signup/login logic.
    - Doctor Dashboard (create slots, view patient bookings, connect Google Calendar status).
    - Patient Dashboard (view doctors list, filter availability slots, view scheduled appointments).
    - Race-condition safe booking endpoint (uses `select_for_update()` in a database transaction to prevent double bookings).
    - Google Calendar OAuth redirect and callback URLs.
    - Asynchronous thread helpers to create Calendar events and request Email Service triggers without blocking page response.
  - Configured core app paths in `core/urls.py` and project paths in `hms/urls.py`.
  - Designed responsive glassmorphic styles in `core/static/core/style.css`.
  - Coded HTML templates: `base.html`, `signup.html`, `login.html`, `doctor_dashboard.html`, and `patient_dashboard.html`.
  - Formulated `email-service` serverless service:
    - `package.json` specifying `serverless-offline`.
    - `serverless.yml` declaring Python runtime and http POST handler.
    - `handler.py` processing signup welcome triggers and booking confirmations, using Python `smtplib` to dispatch emails.
  - Created local Mock SMTP Server at `scratch/smtp_server.py` to log sent email payloads to standard output (bypassing python 3.14 deprecated `smtpd` module).
  - Wrote a concurrent multi-threaded Django unit test in `core/tests.py` verifying that simultaneous booking attempts on a single slot result in exactly 1 booking, raising expected locking errors for concurrent requests.
  - Verified tests pass.

### Prompt 3: Healthcare Redesign & AI Assistant Makeover
- **User Request**: Refactor the frontend to make it look visually appealing, healthcare-related, and integrate an interactive Mini AI Care Assistant.
- **AI Action**:
  - Overwrote `style.css` to introduce a clinical teal and sky-blue gradient scheme with rounded glassmorphism cards and forms.
  - Rewrote `base.html` to replace the heartbeat icon with a medical cross brand SVG, and embedded a floating AI Assistant widget in the bottom right corner of all screens.
  - Coded client-side NLP/keyword-based JavaScript chat logic that simulates typing delay, manages conversation state, responds to healthcare/booking queries, and supports suggestion chips.
  - Refined headers in both the Doctor and Patient dashboard templates to match the new color system.
  - Verified visual styles and interactive assistant functionality (typing delay, response correctness, dashboard display) using the browser subagent, capturing screenshots and logs.
  - Confirmed system integrity by running the Django unit test suite.

