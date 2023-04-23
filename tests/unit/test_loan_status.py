import datetime
import random
from typing import Self
import unittest

from bizlogic.loan.status import LoanStatus, LoanStatusType

from bizlogic.protoc.loan_pb2 import Loan

from google.protobuf.timestamp_pb2 import Timestamp


class TestLoanStatus(unittest.TestCase):
    def test_EXPIRED_UNACCEPTED(self: Self) -> None:
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.datetime.now() + datetime.timedelta(days=1))
        loan = Loan(
            principal_amount=random.choice(range(10)),
            repayment_schedule=[],
            offer_expiry=timestamp,
            accepted=False
        )
        assert LoanStatus.loan_status(loan) == LoanStatusType.EXPIRED_UNACCEPTED


    def test_PENDING_ACCEPTANCE(self: Self) -> None:
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.datetime.now() - datetime.timedelta(days=1))
        loan = Loan(
            principal_amount=random.choice(range(10)),
            repayment_schedule=[],
            offer_expiry=timestamp,
            accepted=False
        )
        assert LoanStatus.loan_status(loan) == LoanStatusType.PENDING_ACCEPTANCE


    def test_expired_ACCEPTED(self: Self) -> None:
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.datetime.now() - datetime.timedelta(days=1))
        loan = Loan(
            principal_amount=random.choice(range(10)),
            repayment_schedule=[],
            offer_expiry=timestamp,
            accepted=True
        )
        assert LoanStatus.loan_status(loan) == LoanStatusType.ACCEPTED


    def test_unexpired_ACCEPTED(self: Self) -> None:
        timestamp = Timestamp()
        timestamp.FromDatetime(datetime.datetime.now() + datetime.timedelta(days=1))
        loan = Loan(
            principal_amount=random.choice(range(10)),
            repayment_schedule=[],
            offer_expiry=timestamp,
            accepted=True
        )
        assert LoanStatus.loan_status(loan) == LoanStatusType.ACCEPTED
