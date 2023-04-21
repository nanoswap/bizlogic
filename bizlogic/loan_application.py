
from typing import Self

from ifpskvs.store import Store
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index

# ipfs filename:
#   application/borrower_<id>/created_<timestamp>

class LoanApplication():
    index: Index

    def __init__(self: Self):
        pass

    def add_loan_application(self: Self):
        pass


    def withdraw_loan_application(self: Self):
        pass


    def check_application_status(self: Self):
        pass
