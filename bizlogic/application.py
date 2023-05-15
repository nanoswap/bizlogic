import time
from typing import Iterator, List, Self
import uuid

from ipfskvs.store import Store  # noqa: I201
from ipfskvs.index import Index  # noqa: I201
from ipfsclient.ipfs import Ipfs  # noqa: I201

from bizlogic.protoc.loan_application_pb2 import LoanApplication
from bizlogic.utils import TestingOnly, Utils, ParserType, GROUP_BY, PARSERS
import pandas as pd

PREFIX = "application"

# ipfs filename:
#   application/borrower_<id>/application_<id>/created_<timestamp>

class LoanApplicationWriter():
    """Loan Application Writer
    
    Create a request to ask for funds. Other users will then run a credit check on you
    and send you loan offers. When the user accepts a loan offer, they can close their
    loan application to tell others they are no longer interested in additional borrowing.
    """
    application_id: str
    borrower: str
    amount_asking: int
    ipfsclient: Ipfs
    data: LoanApplication

    def __init__(self: Self, ipfsclient: Ipfs, borrower: str, amount_asking: int, closed: bool = False) -> None:
        """Constructor"""
        self.application_id = str(uuid.uuid4())
        self.borrower = borrower
        self.ipfsclient = ipfsclient
        self.amount_asking = amount_asking
        self.closed = closed
        self.data = LoanApplication(
            amount_asking=self.amount_asking,
            closed=self.closed
        )
    
    def write(self) -> None:

        self._generate_index()
        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.add()
    
    @TestingOnly.decorator
    def delete(self) -> None:
        # don't need to generate index, just delete the store
        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.delete()
    
    def _generate_index(self) -> None:
        self.index = Index(
            prefix=PREFIX,
            index={
                "borrower": self.borrower,
                "application": self.application_id
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

    def withdraw_loan_application(self: Self) -> None:
        # create a new LoanApplication object with closed=True
        self.data = LoanApplication(
            amount_asking=self.amount_asking,
            closed=True
        )
        self.write()


class LoanApplicationReader():
    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs) -> None:
        self.ipfsclient = ipfsclient

    def query_loan_applications(self: Self, borrower: str = None, open_only=True) -> pd.DataFrame:
        # format query parameters
        index = {
            "borrower": borrower
        } if borrower else {}

        # get all applications from ipfs
        applications = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index=index,
                size=2
            ),
            ipfs=self.ipfsclient,
            reader=LoanApplication()
        )

        # parse applications into a dataframe
        df = Store.to_dataframe(applications, PARSERS[ParserType.LOAN_APPLICATION])

        # filter for most recent applications per loan_id
        df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN_APPLICATION])

        # filter for open applications
        return df[~df['closed']] if open_only else df

    def get_loan_application(self: Self, application_id: str, open_only=False) -> pd.DataFrame:
        # query ipfs
        applications = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "application": application_id
                },
                size=2
            ),
            ipfs=self.ipfsclient,
            reader=LoanApplication()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(applications, PARSERS[ParserType.LOAN_APPLICATION])

        # filter for most recent applications per loan_id
        df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN_APPLICATION])

        # filter for open applications
        return df[~df['closed']] if open_only else df
