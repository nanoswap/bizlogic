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
        all_vouches = list(reader.get_all_vouches())

        # Check if the vouch is in all vouches
        self.assertTrue(any(vouch.index.index["vouchee"] == vouchee and vouch.index.index["voucher"] == voucher for vouch in all_vouches))

        # Clean up
        writer.delete()

    # def test_get_vouchers_for_borrower(self):
    #     vouchee = str(uuid.uuid4())
    #     voucher = str(uuid.uuid4())

    #     # Create a vouch
    #     writer = VouchWriter(self.ipfsclient, vouchee, voucher)
    #     writer.write()

    #     # Get vouchers for the borrower
    #     reader = VouchReader(self.ipfsclient)
    #     vouchers = reader.get_vouchers_for_borrower(vouchee)

    #     # Check if the vouch is in the vouchers
    #     self.assertTrue(vouchers.iloc[0]["voucher"] == voucher and vouchers.iloc[0]["vouchee"] == vouchee)

    #     # Clean up
    #     writer.delete()

    # def test_get_vouchees_for_borrower(self):
    #     vouchee = str(uuid.uuid4())
    #     voucher = str(uuid.uuid4())

    #     # Create a vouch
    #     writer = VouchWriter(self.ipfsclient, vouchee, voucher)
    #     writer.write()

    #     # Get vouchees for the borrower
    #     reader = VouchReader(self.ipfsclient)
    #     vouchees = reader.get_vouchees_for_borrower(voucher)

    #     # Check if the vouch is in the vouchees
    #     self.assertTrue(vouchees.iloc[0]["voucher"] == voucher and vouchees.iloc[0]["vouchee"] == vouchee)

    #     # Clean up
    #     writer.delete()
