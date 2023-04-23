from ipfsclient.ipfs import Ipfs
from typing import Self
from bizlogic.loan import PREFIX
from bizlogic.loan.status import LoanStatus, LoanStatusType
from ipfskvs import Index, Store

from bizlogic.protoc.loan_pb2 import Loan

class LoanReader():
    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs):
        self.ipfsclient = ipfsclient
 
    def get_open_loan_offers(self: Self, borrower: str):
        return self.query_for_status(
            status=LoanStatus.PENDING_ACCEPTANCE,
            index=Index(
                prefix=PREFIX,
                index={
                    "borrower": borrower
                }
            ),
        )

    def query_for_status(self: Self, status: LoanStatusType, index: dict = {}):
        # get all applications from ipfs
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index=index
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
