
import datetime
import time
import uuid
from typing import List, Self

from google.protobuf.timestamp_pb2 import Timestamp

from ifpskvs.store import Store
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index

from protoc.loan_pb2 import Loan, LoanPayment

# ipfs filename:
#   loan/borrower_<id>.lender_<id>/loan_<id>/created_<timestamp>

class Loan():
    store: Store

    def __init__(
            self: Self,
            ipfs: Ipfs,
            borrower: str,
            lender: str,
            principal_amount: int,
            repayment_schedule: List[LoanPayment],
            offer_expiry: datetime.date) -> None:
        """Construct a new unaccepted loan and write it."""
        self.loan_id = str(uuid.uuid4())
        index = Index(
            prefix="loan",
            index={
                "borrower": borrower,
                "lender": lender,
            },
            subindex=Index(
                index={
                    "loan": self.loan_id
                },
                subindex=Index(
                    index={
                        "created": str(time.time_ns())
                    }
                )
            )
        )

        data = Loan(
            principal_amount=principal_amount,
            repayment_schedule=repayment_schedule,
            offer_expiry=offer_expiry,
            accepted=False
        )

        self.store = Store(
            index=index,
            ipfs=ipfs,
            writer=data
        )

        self.store.write()

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
                amount_due=amount_due_each_payment,
                due_date=timestamp
            )
            result.append(loan_payment)


    def accept_terms(self: Self):
        pass


    def check_bid_status(self: Self):
        pass
