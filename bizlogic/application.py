import time
from typing import Self

from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index

from protoc.loan_application_pb2 import LoanApplication

# ipfs filename:
#   application/borrower_<id>/created_<timestamp>

class LoanApplicationWriter():
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
        self._write()

    
    def _write(self):

        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.write()
    
    def _generate_index(self):
        self.index = Index(
            prefix="application",
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
    def __init__(self: Self) -> None:
        pass
