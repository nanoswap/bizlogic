import time
from typing import Self

from ifpskvs.store import Store
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index

from protoc.loan_application_pb2 import LoanApplication

# ipfs filename:
#   application/borrower_<id>/created_<timestamp>

class LoanApplication():
    store: Store

    def __init__(self: Self, borrower: str, amount_asking: int):
        """Constructor"""
        index = Index(
            prefix="application",
            index={
                "borrower": borrower
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

        data = LoanApplication(amount_asking=amount_asking)

        self.store(index=index, ipfs=Ipfs(), write=data)
        self.store.write()

    def add_loan_application(self: Self):
        pass


    def withdraw_loan_application(self: Self):
        pass


    def check_application_status(self: Self):
        pass
