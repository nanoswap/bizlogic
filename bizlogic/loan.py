
import time
import datetime
import uuid
from typing import List, Self

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
            offer_expiry: datetime.date):
        """Construct a new unaccepted loan and write it."""
        index = Index(
            prefix="bid",
            index={
                "borrower": borrower,
                "lender": lender,
            },
            subindex=Index(
                index={
                    "bid": str(uuid.uuid4())
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
    def generate_payment_schedule(self: Self):
        pass

    def add_bid(self: Self):
        pass


    def withdraw_bid(self: Self):
        pass


    def accept_bid(self: Self):
        pass


    def check_bid_status(self: Self):
        pass
