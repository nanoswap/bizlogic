
import datetime
import time
import uuid
from typing import List, Self

from google.protobuf.timestamp_pb2 import Timestamp
from enum import Enum

from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index

from protoc.loan_pb2 import Loan, LoanPayment

PREFIX="loan"

# ipfs filename:
#   loan/borrower_<id>.lender_<id>.loan_<id>/created_<timestamp>

class LoanStatusType(Enum):
    PENDING_ACCEPTANCE = 1
    EXPIRED_UNACCEPTED = 2
    ACCEPTED = 3

class LoanStatus():

    @staticmethod
    def loan_status(loan):
        now = datetime.datetime.now()
        expiry = datetime.datetime.fromtimestamp(loan.offer_expiry.seconds) + datetime.timedelta(microseconds=loan.offer_expiry.nanos / 1000)

        if expiry <= now and not loan.accepted:
            return LoanStatusType.PENDING_ACCEPTANCE

        elif expiry > now and not loan.accepted:
            return LoanStatusType.EXPIRED_UNACCEPTED

        elif expiry <= now and loan.accepted:
            return LoanStatusType.ACCEPTED

        elif expiry > now and loan.accepted:
            return LoanStatusType.ACCEPTED

        raise

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

        store.add()
    
    def _generate_index(self):
        self.index = Index(
            prefix=PREFIX,
            index={
                "borrower": self.borrower,
                "lender": self.lender,
                "loan": self.loan_id
            },
            subindex=Index(
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
    
    def query_for_status(self: Self, status: LoanStatusType):
        # get all applications from ipfs
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={}
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # filter for unexpired and unaccepted loans
        return [
            loan
            for loan in loans
            if LoanStatus.loan_status(loan.reader) == status
        ]

    def query_for_borrower(self: Self, borrower: str):
        return Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "borrower": borrower
                }
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

    def query_for_lender(self: Self, lender: str):
        return Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "lender": lender
                }
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

    def query_for_loan(self: Self, loan_id: str):
        return Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "loan": loan_id
                }
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )
