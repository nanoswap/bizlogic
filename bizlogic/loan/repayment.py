import datetime
import uuid
from typing import List
import math

from bizlogic.protoc.loan_pb2 import LoanPayment

from google.protobuf.timestamp_pb2 import Timestamp


class PaymentSchedule():
    """Payment Schedule Utilities."""
    @staticmethod
    def create_payment_schedule(
            principal: int,
            interest_rate: float,
            start_date: datetime.datetime,
            end_date: datetime.datetime,
            number_of_payments: int) -> List[LoanPayment]:
        """Generate a list of loan payment objects.

        This method will create a schedule of uniformly distributed payments
        from start_date to end_date inclusive.

        Args:
            principal (int): The amount of the loan (before interest)
            interest_rate (float): The interest rate of the loan in decimal
                (ex: 0.05 is 5%)
            start_date (datetime.datetime): Date when the first payment is due.
            end_date (datetime.datetime): Date when the last payment is due.
            number_of_payments (int): The total number of payments to break up
                the loan into. Must be greater than 2.

        Returns:
            List[LoanPayment]: A list of loan payment objects

        Raises:
            ValueError: If the number of payments is not greater than 2.
        """
        if number_of_payments <= 2:
            raise ValueError("Number of payments must be greater than 2")

        # calculate the payment terms
        total_amount_due = principal * (1 + interest_rate)
        amount_due_each_payment = int(
            math.ceil(
                total_amount_due / number_of_payments
            )
        )

        # calculate the duration between each payment
        total_duration = end_date - start_date
        payment_duration = total_duration / (number_of_payments - 1)

        result = []
        for payment_interval in range(number_of_payments):
            # calculate the due date
            due_date = Timestamp()
            if payment_interval == number_of_payments - 1:
                # Set the due_date for the last payment to the end_date
                # (to avoid rounding errors)
                due_date.FromDatetime(end_date)
            else:
                # calculate the due_date for the other payments
                due_date.FromDatetime(
                    start_date + payment_duration * payment_interval
                )

            # format the data
            loan_payment = LoanPayment()
            loan_payment.payment_id = str(uuid.uuid4())
            loan_payment.amount_due = amount_due_each_payment
            loan_payment.due_date.CopyFrom(due_date)

            result.append(loan_payment)

        return result
