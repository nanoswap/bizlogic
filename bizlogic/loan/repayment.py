import datetime
from typing import List
from google.protobuf.timestamp_pb2 import Timestamp
import uuid

from bizlogic.protoc.loan import LoanPayment


class PaymentSchedule():

    @staticmethod
    @staticmethod
    def create_payment_schedule(
            amount: int,
            interest_rate: float,
            total_duration: datetime.timedelta,
            number_of_payments: int) -> List[LoanPayment]:
        """
        Generate a list of loan payment objects based on some initial loan parameters

        Args:
            amount (int): The amount of the loan (before interest)
            interest_rate (float): The interest rate of the loan in decimal (ex: 1.05 is 5%)
            total_duration (datetime.timedelta): The time that the borrower has to finish all repayments
            number_of_payments (int): The number of payments to break up the loan into
        """
        assert interest_rate > 1

        # calculate the payment terms
        total_amount_due = amount * interest_rate
        amount_due_each_payment = int(total_amount_due / number_of_payments)
        first_payment = datetime.datetime.now()

        result = []
        for payment_interval in range(number_of_payments):
            timestamp = Timestamp()
            timestamp.FromDatetime(first_payment + payment_interval * total_duration)
            # format the data
            loan_payment = LoanPayment(
                payment_id=str(uuid.uuid4()),
                amount_due=amount_due_each_payment,
                due_date=timestamp
            )
            result.append(loan_payment)
