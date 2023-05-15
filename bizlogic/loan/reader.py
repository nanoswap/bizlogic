
from typing import Iterator, Self
import pandas as pd

from bizlogic.loan import PREFIX
from bizlogic.loan.status import LoanStatus, LoanStatusType
from bizlogic.protoc.loan_pb2 import Loan
from bizlogic.utils import Utils, ParserType, GROUP_BY, PARSERS

from ipfsclient.ipfs import Ipfs

from ipfskvs.index import Index
from ipfskvs.store import Store


class LoanReader():
    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs) -> None:
        """Constructor."""
        self.ipfsclient = ipfsclient
 
    def get_open_loan_offers(self: Self, borrower: str, recent_only: bool = True) -> pd.DataFrame:
        """Get all open loan offers for a borrower."""
        return self.query_for_status(
            status=LoanStatus.PENDING_ACCEPTANCE,
            index=Index(
                prefix=PREFIX,
                index={
                    "borrower": borrower
                },
                size=3
            ),
            recent_only=recent_only
        )

    def query_for_status(self: Self, status: LoanStatusType, index: dict = {}, recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific status."""
        # get all applications from ipfs
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index=index
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for unexpired and unaccepted loans
        df = df[df['loan_status'] == status]

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_borrower(self: Self, borrower: str, recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific borrower."""
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "borrower": borrower
                },
                size=3
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_lender(self: Self, lender: str, recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific lender."""
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "lender": lender
                },
                size=3
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_loan(self: Self, loan_id: str, recent_only: bool = True) -> pd.DataFrame:
        """Query for a specific loan."""
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "loan": loan_id
                },
                size=3
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

