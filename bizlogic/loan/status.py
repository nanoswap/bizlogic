from datetime import datetime, timezone
from enum import Enum

from bizlogic.protoc.loan_pb2 import Loan


class LoanStatusType(Enum):
    """Loan Status Type."""

    PENDING_ACCEPTANCE = 1
    EXPIRED_UNACCEPTED = 2
    ACCEPTED = 3
    DRAFT = 4


class LoanStatus():
    """Loan Status."""

    @staticmethod
    def loan_status(loan: Loan) -> LoanStatusType:
        """Get the status of a loan.

        Args:
            loan: the loan

        Returns:
            LoanStatusType: the status of the loan
        """
        now = datetime.now(timezone.utc)

        # if the loan has no transaction, it is a draft
        # TODO: check if transaction is valid
        if 'transaction' not in loan.keys():
            return LoanStatusType.DRAFT

        # if the loan has not expired and is not accepted
        elif loan['offer_expiry'] > now and not loan['accepted']:
            return LoanStatusType.PENDING_ACCEPTANCE

        # if the loan has expired and is not accepted
        elif loan['offer_expiry'] <= now and not loan['accepted']:
            return LoanStatusType.EXPIRED_UNACCEPTED

        # if the loan is accepted, regardless of expiry
        elif loan['accepted']:
            return LoanStatusType.ACCEPTED

        raise ValueError("Unable to determine loan status")
