import unittest
import uuid

from ipfsclient.ipfs import Ipfs
from bizlogic.vouch import VouchReader, VouchWriter


class TestVouch(unittest.TestCase):

    def setUp(self):
        self.ipfsclient = Ipfs()  # Initialize your IPFS client here

    def test_vouch_creation(self):
        vouchee = str(uuid.uuid4())
        voucher = str(uuid.uuid4())

        # Create a vouch
        writer = VouchWriter(self.ipfsclient, voucher, vouchee)
        writer.write()

        # Read all vouches
        reader = VouchReader(self.ipfsclient)
        df = reader.get_all_vouches()

        # Check if the vouch is in all vouches
        self.assertFalse(df[df['vouchee'].isin([vouchee])].empty)
        self.assertFalse(df[df['voucher'].isin([voucher])].empty)
        self.assertFalse(df[(df['vouchee'] == vouchee) & (df['voucher'] == voucher)].empty)  # noqa: E501

        # Clean up
        writer.delete()

    def test_query_vouches_for_voucher(self):
        vouchee = str(uuid.uuid4())
        voucher = str(uuid.uuid4())

        # Create a vouch
        writer = VouchWriter(self.ipfsclient, voucher, vouchee)
        writer.write()

        # Query vouches for the voucher
        reader = VouchReader(self.ipfsclient)
        df = reader.query_vouches(voucher=voucher)

        # Check if the vouch is in the query results
        self.assertFalse(df[df['vouchee'].isin([vouchee])].empty)
        self.assertFalse(df[df['voucher'].isin([voucher])].empty)
        self.assertFalse(df[(df['vouchee'] == vouchee) & (df['voucher'] == voucher)].empty)  # noqa: E501

        # Clean up
        writer.delete()

    def test_query_vouches_for_vouchee(self):
        vouchee = str(uuid.uuid4())
        voucher = str(uuid.uuid4())

        # Create a vouch
        writer = VouchWriter(self.ipfsclient, voucher, vouchee)
        writer.write()

        # Query vouches for the vouchee
        reader = VouchReader(self.ipfsclient)
        df = reader.query_vouches(vouchee=vouchee)

        # Check if the vouch is in the query results
        self.assertFalse(df[df['vouchee'].isin([vouchee])].empty)
        self.assertFalse(df[df['voucher'].isin([voucher])].empty)
        self.assertFalse(df[(df['vouchee'] == vouchee) & (df['voucher'] == voucher)].empty)  # noqa: E501

        # Clean up
        writer.delete()
