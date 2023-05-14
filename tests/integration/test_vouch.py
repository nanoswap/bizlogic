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

    def test_get_vouchers_for_borrower(self):
        vouchee = str(uuid.uuid4())
        voucher = str(uuid.uuid4())

        # Create a vouch
        writer = VouchWriter(self.ipfsclient, vouchee, voucher)
        writer.write()

        # Get vouchers for the borrower
        reader = VouchReader(self.ipfsclient)
        df = reader.get_vouchers_for_borrower(vouchee)

        # Check if the vouch is in the vouchers
        self.assertFalse(df[df['vouchee'].isin([voucher])].empty)
        self.assertFalse(df[df['voucher'].isin([vouchee])].empty)
        self.assertFalse(df[(df['vouchee'] == voucher) & (df['voucher'] == vouchee)].empty)  # noqa: E501

        # Clean up
        writer.delete()

    def test_get_vouchees_for_borrower(self):
        vouchee = str(uuid.uuid4())
        voucher = str(uuid.uuid4())

        # Create a vouch
        writer = VouchWriter(self.ipfsclient, vouchee, voucher)
        writer.write()

        # Get vouchees for the borrower
        reader = VouchReader(self.ipfsclient)
        df = reader.get_vouchees_for_borrower(voucher)

        # Check if the vouch is in the vouchees
        self.assertFalse(df[df['vouchee'].isin([voucher])].empty)
        self.assertFalse(df[df['voucher'].isin([vouchee])].empty)
        self.assertFalse(df[(df['vouchee'] == voucher) & (df['voucher'] == vouchee)].empty)  # noqa: E501

        # Clean up
        writer.delete()
