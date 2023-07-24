
from typing import List, Self
import json

from google.protobuf.json_format import MessageToDict

from bizlogic.loan import PREFIX
from bizlogic.loan.status import LoanStatus, LoanStatusType
from bizlogic.protoc.loan_pb2 import Loan
from bizlogic.utils import GROUP_BY, PARSERS, ParserType, Utils

from ipfsclient.ipfs import Ipfs

from ipfskvs.index import Index
from ipfskvs.store import Store

import pandas as pd
import logging

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


class LoanReader():
    """Loan Reader."""

    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs) -> None:
        """Create a Loan Reader."""
        self.ipfsclient = ipfsclient

    def get_open_loan_offers(
            self: Self,
            borrower: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Get all open loan offers for a borrower.

        Args:
            borrower (str): The borrower to get open loan offers for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The open loan offers for the borrower.
        """
        return self.query_for_status(
            status=LoanStatusType.PENDING_ACCEPTANCE,
            index=Index(
                prefix=PREFIX,
                index={
                    "borrower": borrower
                },
                size=3
            ),
            recent_only=recent_only
        )

    def query_for_status(
            self: Self,
            status: LoanStatusType,
            index: dict = {},
            recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific status.  # noqa: D411, D415

        Args:
            status (LoanStatusType): The status to query for.
            index (dict, optional): Additional search/filter options,
                ex {"borrower": 123}. Defaults to {}.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.
        Returns:
            pd.DataFrame: The loans with the specified status.
        """
        # get all applications from ipfs
        loans = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index=index,
                size=3
            ),
            ipfs=self.ipfsclient,
            reader=Loan()
        )

        # parse results into a dataframe
        df = Store.to_dataframe(loans, PARSERS[ParserType.LOAN])
        if df.empty:
            return df

        # filter for unexpired and unaccepted loans
        LOG.debug("Filtering for status: %s", status)
        df['loan_status'] = df.apply(LoanStatus.loan_status, axis=1)
        df = df[df['loan_status'] == status]
        if df.empty:
            return df

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_borrower(
            self: Self,
            borrower: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific borrower.

        Args:
            borrower (str): The borrower to query for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The loans with the specified borrower.
        """
        # fetch the loan data from ipfs
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
        if df.empty:
            return df

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_lender(
            self: Self,
            lender: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Query for loans with a specific lender.

        Args:
            lender (str): The lender to query for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The loans with the specified lender.
        """
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
        if df.empty:
            return df

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_loan(
            self: Self,
            loan_id: str,
            recent_only: bool = True) -> pd.DataFrame:
        """Query for a specific loan.

        Args:
            loan_id (str): The loan to query for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            pd.DataFrame: The loan with the specified id.
        """
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
        if df.empty:
            return df

        # filter for most recent applications per loan_id
        if recent_only:
            df = Utils.get_most_recent(df, GROUP_BY[ParserType.LOAN])

        return df

    def query_for_loan_details(
            self: Self,
            loan_id: str,
            recent_only: bool = True) -> List[Loan]:
        """Query for a specific loan and return all the loan data.

        Args:
            loan_id (str): The loan to query for.
            recent_only (bool, optional): Include previous updates or
                only get the most recent. Defaults to True.

        Returns:
            str: The loan with the specified id in JSON format.
        """
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

        loan_data = []
        for loan in loans:
            # convert the protobuf message to a Python dict
            loan_dict = MessageToDict(loan.reader)

            # extract and add metadata to the loan dictionary
            metadata = loan.index.get_metadata()
            loan_dict["metadata"] = metadata

            loan_data.append(loan_dict)

        # if recent_only is set to True, only return the most recent loan data
        LOG.debug("Loan details: %s", loan_data)
        if recent_only and loan_data:
            loan_data = [max(loan_data, key=lambda row: row['metadata'].get('created', ''))]

        return loan_data
