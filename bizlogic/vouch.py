import time
import uuid
import pandas as pd
from typing import Iterator, Self
from bizlogic.utils import TestingOnly
# "voucher": person giving the vouch
# "vouchee": person receiving the vouch

# ipfs filename:
#   vouch/vouchee_<id>.voucher_<id>/created_<timestamp>

from ipfskvs.index import Index
from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs

from bizlogic.protoc.vouch_pb2 import Vouch
from bizlogic.utils import TestingOnly, Utils, ParserType, GROUP_BY, PARSERS

PREFIX = "vouch"


class VouchWriter():
    vouch_id: str
    vouchee: str
    voucher: str
    ipfsclient: Ipfs
    data: Vouch

    def __init__(
            self: Self,
            ipfsclient: Ipfs,
            voucher: str,
            vouchee: str) -> None:
        """Constructor"""
        self.vouch_id = str(uuid.uuid4())
        self.vouchee = vouchee
        self.voucher = voucher
        self.ipfsclient = ipfsclient
        self.data = Vouch(active=True)

    def write(self: Self) -> None:
        self._generate_index()

        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.add()
    
    @TestingOnly.decorator
    def delete(self):
        # don't need to generate index, just delete the store
        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.delete()

    def _generate_index(self: Self) -> None:
        self.index = Index(
            prefix=PREFIX,
            index={
                "vouchee": self.vouchee,
                "voucher": self.voucher,
                "vouch": self.vouch_id
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

class VouchReader():
    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs) -> None:
        self.ipfsclient = ipfsclient

    def get_all_vouches(self: Self) -> Iterator[Store]:
        query_results = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={}
            ),
            ipfs=self.ipfsclient,
            reader=Vouch()
        )

        # parse applications into a dataframe
        df = Store.to_dataframe(query_results, PARSERS[ParserType.VOUCH])

        # filter for most recent applications per loan_id
        return Utils.get_most_recent(df, GROUP_BY[ParserType.VOUCH])

    def get_vouchers_for_borrower(
        self: Self,
        borrower: str
    ) -> pd.DataFrame:
        query_results = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "voucher": borrower
                },
                size=2
            ),
            ipfs=self.ipfsclient,
            reader=Vouch()
        )

        # parse applications into a dataframe
        df = Store.to_dataframe(query_results, PARSERS[ParserType.VOUCH])

        # filter for most recent applications per loan_id
        return Utils.get_most_recent(df, GROUP_BY[ParserType.VOUCH])

    def get_vouchees_for_borrower(
        self: Self,
        borrower: str
    ) -> Iterator[Store]:
        query_results = Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "vouchee": borrower
                },
                size=2
            ),
            ipfs=self.ipfsclient,
            reader=Vouch()
        )

        # parse applications into a dataframe
        df = Store.to_dataframe(query_results, PARSERS[ParserType.VOUCH])

        # filter for most recent applications per loan_id
        return Utils.get_most_recent(df, GROUP_BY[ParserType.VOUCH])
