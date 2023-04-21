
import datetime
import time
import uuid
from typing import List, Self

from google.protobuf.timestamp_pb2 import Timestamp

from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index

from protoc.loan_pb2 import Loan, LoanPayment

# ipfs filename:
#   loan/borrower_<id>.lender_<id>/loan_<id>/created_<timestamp>

class LoanWriter():
    loan_id: str
    borrower: str
    lender: str
    index: Index
    data: Loan
    ipfsclient: Ipfs

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
        self.borrower = borrower
        self.lender = lender
        self._generate_index()
        self.ipfsclient = ipfs
        self.data = Loan(
            principal_amount=principal_amount,
            repayment_schedule=repayment_schedule,
            offer_expiry=offer_expiry,
            accepted=False
        )

    
    def _write(self):

        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.write()
    
    def _generate_index(self):
        self.index = Index(
            prefix="loan",
            index={
                "borrower": self.borrower,
                "lender": self.lender,
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


    def accept_terms(self: Self):
        self.data = Loan(
            principal_amount=self.data.principal_amount,
            repayment_schedule=self.data.repayment_schedule,
            offer_expiry=self.data.offer_expiry,
            accepted=True
        )
        self._generate_index()
        self._write()


    def check_bid_status(self: Self):
        now = datetime.datetime.now()
        if self.data.offer_expiry <= now and not self.data.accepted:
            return "PENDING_ACCEPTANCE"
        
        elif self.data.offer_expiry > now and not self.data.accepted:
            return "EXPIRED_UNACCEPTED"
        
        elif self.data.offer_expiry <= now and self.data.accepted:
            return "ACCEPTED"
        
        elif self.data.offer_expiry > now and self.data.accepted:
            return "ACCEPTED"

        raise

    def register_payment(self: Self, payment_id: str, transaction: str):
        new_repayment_schedule = []
        for payment in self.data.repayment_schedule:
            if payment.payment_id == payment_id:
                new_repayment_schedule.append(LoanPayment(
                    payment_id=payment_id,
                    amount_due=payment.amount_due_each_payment,
                    due_date=payment.timestamp,
                    transaction=transaction
                ))
            else:
                new_repayment_schedule.append(payment)
        
        self.data = Loan(
            principal_amount=self.data.principal_amount,
            repayment_schedule=self.data.repayment_schedule,
            offer_expiry=self.data.offer_expiry,
            accepted=self.data.accepted
        )
        self._generate_index()
        self._write()


class LoanReader():
    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs):
        self.ipfsclient = ipfsclient
    
    def get_loan_offers(self: Self):
        pass

    def get_loans_for_borrower(self: Self, borrower: str):
        pass

    def get_loans_for_lender(self: Self, lender: str):
        pass

    def get_payments_for_loan(self: Self, loan_id: str):
        pass
