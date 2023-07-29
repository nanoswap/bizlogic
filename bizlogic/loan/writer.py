
import datetime
import time
import uuid
from typing import List, Self

from bizlogic.loan import PREFIX
from bizlogic.protoc.loan_pb2 import Loan, LoanPayment

from google.protobuf.timestamp_pb2 import Timestamp

from ipfsclient.ipfs import Ipfs

from ipfskvs.index import Index
from ipfskvs.store import Store
from nanohelp.secret import SecretManager
from nanohelp.wallet import WalletManager


class LoanWriter():
    """Loan Writer.

    ipfs filename:
        loan/borrower_<id>.lender_<id>.loan_<id>/created_<timestamp>
    """

    loan_id: str
    borrower: str
    lender: str
    index: Index
    data: Loan
    ipfsclient: Ipfs

    def __init__(
            self: Self,
            ipfs: Ipfs,
            borrower: str,
            lender: str,
            principal_amount: int,
            repayment_schedule: List[LoanPayment],
            offer_expiry: datetime.date,
            secret_manager: SecretManager,
            project: str) -> None:
        """Construct a new unaccepted loan and write it.

        The loan is not accepted until the borrower signs it.

        Args:
            ipfs: the ipfs client
            borrower: the borrower id
            lender: the lender id
            principal_amount: the principal amount of the loan
            repayment_schedule: the repayment schedule of the loan
            offer_expiry: the expiry date of the loan offer
            secret_manager: the secret manager to use for
                storing wallet private keys
            project: the project to use for wallet creation (the project to
                use in Google Secret Manager for storing the private keys
                of the created wallets)
        """
        self.loan_id = str(uuid.uuid4())
        self.borrower = borrower
        self.lender = lender
        self.ipfsclient = ipfs
        timestamp = Timestamp()
        timestamp.FromDatetime(offer_expiry)
        self.data = Loan(
            principal_amount=principal_amount,
            repayment_schedule=repayment_schedule,
            offer_expiry=timestamp,
            accepted=False
        )

        # Create deposit wallets
        self.create_wallets(secret_manager, project)

    @staticmethod
    def from_data(
            ipfs: Ipfs,
            data: Store,
            wallet_manager: WalletManager,
            secret_manager: SecretManager,
            project: str) -> Self:
        """Construct a new loan from existing data.

        Args:
            ipfs: the ipfs client
            data: the loan data
            wallet_manager: the wallet manager
            secret_manager: the secret manager to use for
                storing wallet private keys
            project: the project to use for wallet creation (the project to
                use in Google Secret Manager for storing the private keys
                of the created wallets)

        Returns:
            LoanWriter: the loan writer
        """
        writer = LoanWriter(
            ipfs=ipfs,
            borrower=data.index["borrower"],
            lender=data.index["lender"],
            principal_amount=data.reader.principal_amount,
            repayment_schedule=data.reader.repayment_schedule,
            offer_expiry=data.reader.offer_expiry,
            wallet_manager=wallet_manager,
            secret_manager=secret_manager
        )
        # Create deposit wallets
        writer.create_wallets(secret_manager, project)

        return writer

    def create_wallets(
            self: Self,
            secret_manager: SecretManager,
            project: str) -> None:
        """Create deposit wallets for borrower and lender.

        The borrower deposit wallet is for the principal and
        the lender deposit wallet is for the repayments.

        Args:
            secret_manager: the secret manager to use for
                storing wallet private keys
            project: the project to use for wallet creation (the project to
                use in Google Secret Manager for storing the private keys
                of the created wallets)
        """
        # Borrower's deposit wallet
        borrower_wallet_name = f"{self.loan_id}_borrower_deposit_wallet"
        borrower_wallet_id, borrower_account_address = \
            WalletManager(secret_manager).create_wallet(
                project, borrower_wallet_name
            )

        # Lender's deposit wallet
        lender_wallet_name = f"{self.loan_id}_lender_deposit_wallet"
        lender_wallet_id, lender_account_address = \
            WalletManager(secret_manager).create_wallet(
                project, lender_wallet_name
            )

        # Check if wallets created successfully
        if not borrower_wallet_id or not lender_wallet_id:
            raise Exception("Error during wallets creation. Loan initiation failed.")

    def write(self: Self) -> None:
        """Write the loan to IPFS."""
        self._generate_index()

        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.add()

    def _generate_index(self: Self) -> None:
        """Generate the index for the loan."""
        self.index = Index(
            prefix=PREFIX,
            index={
                "borrower": self.borrower,
                "lender": self.lender,
                "loan": self.loan_id
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

    def accept_terms(self: Self) -> None:
        """Accept the loan terms."""
        self.data = Loan(
            principal_amount=self.data.principal_amount,
            repayment_schedule=self.data.repayment_schedule,
            offer_expiry=self.data.offer_expiry,
            accepted=True
        )

    def register_payment(
            self: Self,
            payment_id: str,
            transaction: str) -> None:
        """Register a payment.

        Args:
            payment_id: the payment id
            transaction: the transaction id
        """
        new_repayment_schedule = []
        for payment in self.data.repayment_schedule:
            if payment.payment_id == payment_id:
                new_repayment_schedule.append(LoanPayment(
                    payment_id=payment_id,
                    amount_due=payment.amount_due_each_payment,
                    due_date=payment.timestamp,
                    transaction=transaction
                ))
            else:
                new_repayment_schedule.append(payment)

        self.data = Loan(
            principal_amount=self.data.principal_amount,
            repayment_schedule=self.data.repayment_schedule,
            offer_expiry=self.data.offer_expiry,
            accepted=self.data.accepted
        )
