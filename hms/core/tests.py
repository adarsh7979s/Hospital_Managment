import threading
from django.test import TransactionTestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import UserProfile, AvailabilitySlot, Booking

class BookingRaceConditionTest(TransactionTestCase):
    def setUp(self):
        # Create doctor
        self.doctor = User.objects.create_user(username='doctor_test', email='doc@test.com', password='password')
        UserProfile.objects.create(user=self.doctor, role='doctor')
        
        # Create patients
        self.patient1 = User.objects.create_user(username='patient1', email='p1@test.com', password='password')
        UserProfile.objects.create(user=self.patient1, role='patient')
        
        self.patient2 = User.objects.create_user(username='patient2', email='p2@test.com', password='password')
        UserProfile.objects.create(user=self.patient2, role='patient')
        
        # Create slot in the future
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        self.slot = AvailabilitySlot.objects.create(
            doctor=self.doctor,
            start_time=start_time,
            end_time=end_time
        )

    def test_simultaneous_booking_race_condition(self):
        results = []
        errors = []

        def book_slot_thread(user):
            from django.db import transaction, OperationalError
            try:
                # Wrap in database transaction
                with transaction.atomic():
                    # select_for_update locks the record
                    slot = AvailabilitySlot.objects.select_for_update().get(id=self.slot.id)
                    if slot.is_booked:
                        errors.append(f"{user.username}: Already booked")
                        return
                    
                    # Simulate slight delay to increase race chance
                    import time
                    time.sleep(0.1)

                    Booking.objects.create(patient=user, slot=slot)
                    slot.is_booked = True
                    slot.save()
                    results.append(user.username)
            except OperationalError as oe:
                # Under SQLite, concurrent write requests will trigger a database lock error
                errors.append(f"{user.username}: Database locked ({oe})")
            except Exception as e:
                errors.append(f"{user.username}: Error ({e})")

        # Launch threads simultaneously
        t1 = threading.Thread(target=book_slot_thread, args=(self.patient1,))
        t2 = threading.Thread(target=book_slot_thread, args=(self.patient2,))

        t1.start()
        t2.start()
        t1.join()
        t2.join()

        # Check total bookings in database: Must be exactly 1
        bookings = Booking.objects.filter(slot=self.slot)
        self.assertEqual(bookings.count(), 1)
        
        # The slot state must be booked in DB
        self.slot.refresh_from_db()
        self.assertTrue(self.slot.is_booked)
        
        print(f"\n[Test Output] Successful booking by: {results}")
        print(f"[Test Output] Blocked attempts / errors: {errors}\n")
