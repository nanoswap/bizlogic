import unittest
from unittest.mock import MagicMock
import pandas as pd

from bizlogic.loan.reader import LoanReader
from bizlogic.loan.status import LoanStatusType
from bizlogic.loan import PREFIX
from ipfskvs.index import Index

class TestLoanReader(unittest.TestCase):

    def setUp(self):
        self.loan_reader = LoanReader(ipfsclient=MagicMock())
        self.borrower_id = '123'
        self.status = LoanStatusType.PENDING_ACCEPTANCE
        self.index = Index(
            prefix=PREFIX,
            index={"borrower": self.borrower_id},
            size=3,
            subindex=None
        )

    def test_get_open_loan_offers(self):
        self.loan_reader.query_for_status = MagicMock(return_value=pd.DataFrame())
        result = self.loan_reader.get_open_loan_offers(self.borrower_id)
        self.loan_reader.query_for_status.assert_called_with(status=self.status, index=self.index, recent_only=True)
        self.assertIsInstance(result, pd.DataFrame)

    def test_query_for_status(self):
        self.loan_reader.query_for_status = MagicMock(return_value=pd.DataFrame())
        result = self.loan_reader.query_for_status(status=self.status, index=self.index)
        self.assertIsInstance(result, pd.DataFrame)

    def test_query_for_borrower(self):
        self.loan_reader.query_for_borrower = MagicMock(return_value=pd.DataFrame())
        result = self.loan_reader.query_for_borrower(self.borrower_id)
        self.assertIsInstance(result, pd.DataFrame)

    def test_query_for_lender(self):
        self.loan_reader.query_for_lender = MagicMock(return_value=pd.DataFrame())
        result = self.loan_reader.query_for_lender(self.borrower_id)
        self.assertIsInstance(result, pd.DataFrame)

    def test_query_for_loan(self):
        self.loan_reader.query_for_loan = MagicMock(return_value=pd.DataFrame())
        result = self.loan_reader.query_for_loan(self.borrower_id)
        self.assertIsInstance(result, pd.DataFrame)

    def test_query_for_loan_details(self):
        self.loan_reader.query_for_loan_details = MagicMock(return_value='[]')
        result = self.loan_reader.query_for_loan_details(self.borrower_id)
        self.assertIsInstance(result, str)
