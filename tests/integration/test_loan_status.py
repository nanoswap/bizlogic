"""Test LoanReader.query_for_status()."""

from typing import Self

import unittest
import uuid

from bizlogic.loan.reader import LoanReader
from bizlogic.loan.writer import LoanWriter

from ipfsclient.ipfs import Ipfs


class TestLoanStatus(unittest.TestCase):
    """Test LoanReader.query_for_status()."""

    def setUp(self: Self) -> None:
        """Set up the test."""
        self.ipfs = Ipfs()
        self.loan_reader = LoanReader(self.ipfs)
        self.loan_writer = LoanWriter(
            ipfsclient=self.ipfs,
            borrower=str(uuid.uuid4()),
            lender=str(uuid.uuid4()),
            amount=1000,

        )
