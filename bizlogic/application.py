import time
from typing import List, Self

from ipfskvs.store import Store  # noqa: I201
from ipfskvs.index import Index  # noqa: I201
from ipfsclient.ipfs import Ipfs  # noqa: I201

from bizlogic.protoc.loan_application_pb2 import LoanApplication

PREFIX = "application"

# ipfs filename:
#   application/borrower_<id>/created_<timestamp>

class LoanApplicationWriter():
    """Loan Application Writer
    
    Create a request to ask for funds. Other users will then run a credit check on you
    and send you loan offers. When the user accepts a loan offer, they can close their
    loan application to tell others they are no longer interested in additional borrowing.
    """
    borrower: str
    amount_asking: int
    ipfsclient: Ipfs
    data: LoanApplication

    def __init__(self: Self, ipfsclient: Ipfs, borrower: str, amount_asking: int):
        """Constructor"""
        self.borrower = borrower
        self.ipfsclient = ipfsclient
        self.amount_asking = amount_asking
        self.data = LoanApplication(
            amount_asking=self.amount_asking,
            closed=False
        )
        self._generate_index()

    
    def write(self):

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
                "borrower": self.borrower
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

    def withdraw_loan_application(self: Self):
        self.data = LoanApplication(
            amount_asking=self.amount_asking,
            closed=True
        )
        self._generate_index()
        self._write()


class LoanApplicationReader():
    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs):
        self.ipfsclient = ipfsclient

    def get_open_loan_applications(self: Self) -> List[LoanApplication]:
        # get all applications from ipfs
        applications = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={}
            ),
            ipfs=self.ipfsclient,
            reader=LoanApplication()
        )

        # filter for open applications
        return [
            application
            for application in applications
            if not application.reader.closed
        ]
