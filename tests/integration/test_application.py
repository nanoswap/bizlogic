import unittest
from unittest.mock import MagicMock

import uuid
from ipfsclient.ipfs import Ipfs
from bizlogic.application import LoanApplicationWriter, LoanApplicationReader


class TestApplication(unittest.TestCase):
    
    def setUp(self):
        self.ipfsclient = Ipfs()
    
    def read_side_effect(store, data):
        store.reader = [data]

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

    # def test_withdraw(self):
    #     # create an application
    #     writer = LoanApplicationWriter(self.ipfsclient, "John", 1000)
    #     writer.write()
        
    #     # query it, check that it's there
    #     reader = LoanApplicationReader(self.ipfsclient)
    #     # mock the reader to read the application
    #     applications = reader.get_open_loan_applications()

    #     self.assertEqual(len(applications), 1)
    #     self.assertEqual(applications[0].amount_asking, 1000)
    #     self.assertFalse(applications[0].closed)

    #     # withdraw it
    #     writer.withdraw_loan_application()

    #     # query it, check that it's not there
    #     reader = LoanApplicationReader(self.ipfsclient)
    #     applications = reader.get_open_loan_applications()
    #     self.assertEqual(len(applications), 0)

    #     # delete it
    #     writer.delete_loan_application()

    # def test_filter(self):
    #     # create 10 applications
    #     writers = []
    #     for i in range(10):
    #         writer = LoanApplicationWriter(self.ipfsclient, "John", 1000 + i)
    #         writer.write()
    #         writers.append(writer)

    #     # withdraw 3 of them
    #     for writer in writers[:3]:
    #         writer.withdraw_loan_application()

    #     # confirm that there are 7 open applications
    #     reader = LoanApplicationReader(self.ipfsclient)
    #     applications = reader.get_open_loan_applications()

    #     self.assertEqual(len(applications), 7)
    #     amounts = [app.amount_asking for app in applications]
    #     self.assertEqual(set(amounts), set(range(1003, 1011)))

    #     # delete them
    #     for writer in writers:
    #         writer.delete_loan_application()
