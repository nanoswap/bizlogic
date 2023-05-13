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
        applications = list(reader.get_loan_applications_for_borrower(user))

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].reader.amount_asking, 1000)
        self.assertFalse(applications[0].reader.closed)

        # delete it
        writer.delete()

    def test_withdraw(self):
        # create an application
        user = str(uuid.uuid4())
        writer = LoanApplicationWriter(self.ipfsclient, user, 1000)
        writer.write()
        
        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        # mock the reader to read the application
        applications = list(reader.get_loan_applications_for_borrower(user))

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].reader.amount_asking, 1000)
        self.assertFalse(applications[0].reader.closed)

        # withdraw it
        writer1 = copy.deepcopy(writer)  # save to delete later
        writer.withdraw_loan_application()

        # query it, check that it's not there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = list(reader.get_loan_applications_for_borrower(user))
        
        # There should be two applications, one open and one closed,
        # with the same application id, but different timestamps.
        # The closed one should be more recent.
        print([app.index.to_dict() for app in applications])
        print([app.reader for app in applications])
        self.assertEqual(len(applications), 2)
        open_applications = [app for app in applications if not app.reader.closed]
        closed_applications = [app for app in applications if app.reader.closed]
        self.assertEqual(len(open_applications), 1)
        self.assertEqual(len(closed_applications), 1)
        self.assertGreater(closed_applications[0].index.subindex.index["created"], open_applications[0].index.subindex.index["created"])

        # delete it
        writer1.delete()
        writer.delete()

    def test_filter(self):
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
            amounts_expected.remove(writer.amount_asking)
            writer2 = copy.deepcopy(writer)  # save to delete later
            writer2.withdraw_loan_application()
            writers.append(writer2)

        # confirm that there are 7 open applications
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.get_open_loan_applications()

        self.assertEqual(len(applications), 7)
        amounts_actual = [row.amount_asking for _, row in applications.iterrows()]
        self.assertEqual(set(amounts_actual), set(amounts_expected))

        # delete them
        for writer in writers:
            writer.delete()
