
import datetime
import time
import uuid
from typing import List, Self

from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index

from bizlogic.protoc.loan_pb2 import Loan, LoanPayment
from bizlogic.loan import PREFIX


# ipfs filename:
#   loan/borrower_<id>.lender_<id>.loan_<id>/created_<timestamp>



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
        self.ipfsclient = ipfs
        self.data = Loan(
            principal_amount=principal_amount,
            repayment_schedule=repayment_schedule,
            offer_expiry=offer_expiry,
            accepted=False
        )

    @staticmethod
    def from_data(ipfs: Ipfs, data: Store):
        return LoanWriter(
            ipfs=ipfs,
            borrower=data.index["borrower"],
            lender=data.index["lender"],
            principal_amount=data.reader.principal_amount,
            repayment_schedule=data.reader.repayment_schedule,
            offer_expiry=data.reader.offer_expiry
        )

    def write(self):
        self._generate_index()

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

    def accept_terms(self: Self):
        self.data = Loan(
            principal_amount=self.data.principal_amount,
            repayment_schedule=self.data.repayment_schedule,
            offer_expiry=self.data.offer_expiry,
            accepted=True
        )

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

