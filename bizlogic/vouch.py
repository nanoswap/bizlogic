import time
from typing import Self
# "voucher": person giving the vouch
# "vouchee": person receiving the vouch

# ipfs filename:
#   vouch/vouchee_<id>.voucher_<id>/created_<timestamp>

from ipfskvs.index import Index
from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs

from protoc.vouch_pb2 import Vouch

PREFIX = "vouch"


class VouchWriter():
    store: Store

    def __init__(
            self: Self,
            voucher: str,
            vouchee: str,
            amount_asking: int,
            ipfsclient: Ipfs) -> None:
        """Constructor"""
        index = Index(
            prefix=PREFIX,
            index={
                "vouchee": vouchee,
                "voucher": voucher
            },
            subindex=Index(
                index={
                    "created": str(time.time_ns())
                }
            )
        )

        data = Vouch(amount_asking=amount_asking)
        self.store(index=index, ipfs=ipfsclient, writer=data)
        self.store.add()

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
