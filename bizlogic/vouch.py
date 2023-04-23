import time
from typing import Self
# "voucher": person giving the vouch
# "vouchee": person receiving the vouch

# ipfs filename:
#   vouch/vouchee_<id>.voucher_<id>/created_<timestamp>

from ipfskvs.index import Index
from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs

from bizlogic.protoc.vouch_pb2 import Vouch

PREFIX = "vouch"


class VouchWriter():
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
        self.vouchee = vouchee
        self.voucher = voucher
        self.ipfsclient = ipfsclient
        self.data = Vouch(voucher=voucher)

    def write(self: Self):
        self._generate_index()

        store = Store(
            index=self.index,
            ipfs=self.ipfsclient,
            writer=self.data
        )

        store.add()
    
    def _generate_index(self: Self):
        self.index = Index(
            prefix=PREFIX,
            index={
                "vouchee": self.vouchee,
                "voucher": self.voucher
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

class VouchReader():
    ipfsclient: Ipfs

    def __init__(self: Self, ipfsclient: Ipfs):
        self.ipfsclient = ipfsclient

    def get_vouchers_for_borrower(self: Self, borrower: str):
        return Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "voucher": borrower
                }
            ),
            ipfs=self.ipfsclient,
            reader=Vouch()
        )

    def get_vouchees_for_borrower(self: Self, borrower: str):
        return Store.query(
            query_index=Index(
                prefix=PREFIX,
                index={
                    "vouchee": borrower
                }
            ),
            ipfs=self.ipfsclient,
            reader=Vouch()
        )
