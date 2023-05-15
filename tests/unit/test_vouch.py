import unittest
from typing import Self, List
from unittest.mock import MagicMock
from bizlogic.protoc.vouch_pb2 import Vouch
from ipfsclient.ipfs import Ipfs
from ipfskvs.index import Index
from ipfskvs.store import Store
from bizlogic.vouch import VouchReader, VouchWriter


class TestVouchWriter(unittest.TestCase):
    def setUp(self: Self) -> None:
        self.ipfs = Ipfs()
        self.voucher = "0x1111111111111111111111111111111111111111"
        self.vouchee = "0x2222222222222222222222222222222222222222"
        self.writer = VouchWriter(
            ipfsclient=self.ipfs,
            voucher=self.voucher,
            vouchee=self.vouchee
        )

    def test_generate_index(self: Self) -> None:
        self.writer._generate_index()
        self.assertIsInstance(self.writer.index, Index)

    def test_write(self: Self) -> None:
        mock_store = MagicMock(return_value=None)
        with unittest.mock.patch('ipfskvs.store.Store.add', mock_store):
            self.writer.write()

        mock_store.assert_called_once()
