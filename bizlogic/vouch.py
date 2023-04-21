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
            prefix="application",
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
        self.store.write()
