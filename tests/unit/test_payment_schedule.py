import unittest
from datetime import datetime, timedelta
from bizlogic.loan.repayment import PaymentSchedule, LoanPayment
import math

class TestPaymentSchedule(unittest.TestCase):

    def test_create_payment_schedule(self):
        principal = 1000
        interest_rate = 0.05
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 1)
        number_of_payments = 12

        payment_schedule = PaymentSchedule.create_payment_schedule(
            principal, interest_rate, start_date, end_date, number_of_payments
        )

        self.assertEqual(len(payment_schedule), number_of_payments)
        self.assertEqual(payment_schedule[0].due_date.ToDatetime(), start_date)
        self.assertEqual(payment_schedule[-1].due_date.ToDatetime(), end_date)
        self.assertEqual(payment_schedule[0].amount_due, int(math.ceil(1050/number_of_payments)))

        for i in range(len(payment_schedule) - 1):
            duration = payment_schedule[i+1].due_date.ToDatetime() - payment_schedule[i].due_date.ToDatetime()
            # Check that duration is approximately 30 days
            self.assertTrue(timedelta(days=29) < duration < timedelta(days=31))

    def test_create_payment_schedule_with_invalid_number_of_payments(self):
        principal = 1000
        interest_rate = 0.05
        start_date = datetime(2023, 1, 1)
        end_date = datetime(2023, 12, 1)
        number_of_payments = 2

        with self.assertRaises(ValueError):
            PaymentSchedule.create_payment_schedule(
                principal, interest_rate, start_date, end_date, number_of_payments
            )
