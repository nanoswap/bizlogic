
from google.protobuf.timestamp_pb2 import Timestamp
from enum import Enum
from datetime import datetime, timedelta

from bizlogic.protoc.loan import Loan


class LoanStatusType(Enum):
    PENDING_ACCEPTANCE = 1
    EXPIRED_UNACCEPTED = 2
    ACCEPTED = 3


class LoanStatus():

    @staticmethod
    def _timestamp_to_datetime(timestamp: Timestamp) -> datetime:
        seconds = datetime.fromtimestamp(timestamp.seconds)
        micros = timedelta(microseconds=timestamp.nanos / 1000)
        return seconds + micros


    @staticmethod
    def loan_status(loan: Loan):
        now = datetime.now()
        expiry = LoanStatus._timestamp_to_datetime(loan.offer_expiry)

        if expiry <= now and not loan.accepted:
            return LoanStatusType.PENDING_ACCEPTANCE

        elif expiry > now and not loan.accepted:
            return LoanStatusType.EXPIRED_UNACCEPTED

        elif expiry <= now and loan.accepted:
            return LoanStatusType.ACCEPTED

        elif expiry > now and loan.accepted:
            return LoanStatusType.ACCEPTED

        raise
