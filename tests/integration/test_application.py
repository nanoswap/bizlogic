import copy
import unittest
from unittest.mock import MagicMock

import uuid
from ipfsclient.ipfs import Ipfs
from bizlogic.application import LoanApplicationWriter, LoanApplicationReader
from bizlogic.utils import TestingOnly

TestingOnly.testing_mode = True


class TestApplication(unittest.TestCase):
    
    def setUp(self):
        self.ipfsclient = Ipfs()

    def test_read_write(self):
        # create an application
        user = str(uuid.uuid4())
        writer = LoanApplicationWriter(self.ipfsclient, user, 1000)
        writer.write()
        
        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.query_loan_applications(borrower=user)

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications.iloc[0].amount_asking, 1000)
        self.assertFalse(applications.iloc[0].closed)

        # delete it
        writer.delete()

    def test_withdraw_single(self):
        # create an application
        user = str(uuid.uuid4())
        writer = LoanApplicationWriter(self.ipfsclient, user, 1000)
        writer.write()
        
        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.query_loan_applications(borrower=user)

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications.iloc[0].amount_asking, 1000)
        self.assertFalse(applications.iloc[0].closed)

        # withdraw it
        writer1 = copy.deepcopy(writer)  # save to delete later
        writer.withdraw_loan_application()

        # query it, check that it's not there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.query_loan_applications(borrower=user, open_only=False)
        
        self.assertEqual(len(applications), 1)
        open_applications = applications[applications.closed == False]
        closed_applications = applications[applications.closed == True]
        self.assertEqual(len(open_applications), 0)
        self.assertEqual(len(closed_applications), 1)
        self.assertEqual(closed_applications.iloc[0].amount_asking, 1000)

        # delete it
        writer1.delete()
        writer.delete()

    def test_get_open_loan_applications(self):
        # create 10 applications
        writers = []
        amounts_expected = []
        for i in range(10):
            user = str(uuid.uuid4())
            writer = LoanApplicationWriter(self.ipfsclient, user, 1000 + i)
            amounts_expected.append(1000 + i)
            writer.write()
            writers.append(writer)

        # withdraw 3 of them
        for writer in writers[:3]:
            writers.append(copy.deepcopy(writer)) # save to delete later
            amounts_expected.remove(writer.amount_asking)
            writer.withdraw_loan_application()

        # confirm that there are 7 open applications
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.query_loan_applications(open_only=True)

        self.assertEqual(len(applications), 7)
        amounts_actual = applications.amount_asking.tolist()
        self.assertEqual(set(amounts_actual), set(amounts_expected))

        # delete them
        for writer in writers:
            writer.delete()

    def test_get_loan_applications_for_borrower(self):
        # create an application for a borrower
        borrower = str(uuid.uuid4())
        writer = LoanApplicationWriter(self.ipfsclient, borrower, 1000)
        writer.write()

        # create an application for a different borrower
        borrower2 = str(uuid.uuid4())
        writer2 = LoanApplicationWriter(self.ipfsclient, borrower2, 1001)
        writer2.write()

        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.query_loan_applications(borrower=borrower)

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications.iloc[0].amount_asking, 1000)

        # delete them
        writer.delete()
        writer2.delete()
