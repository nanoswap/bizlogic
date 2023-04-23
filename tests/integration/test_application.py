import unittest
from ipfskvs.store import Store
from ipfsclient.ipfs import Ipfs
from bizlogic.protoc.loan_application_pb2 import LoanApplication
from ipfskvs.index import Index
from bizlogic.application import LoanApplicationWriter, LoanApplicationReader
import time


class TestApplication(unittest.TestCase):
    
    def setUp(self):
        self.ipfsclient = Ipfs()

    def test_read_write(self):
        # create an application
        writer = LoanApplicationWriter(self.ipfsclient, "John", 1000)
        
        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.get_open_loan_applications()
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].amount_asking, 1000)
        self.assertFalse(applications[0].closed)

    def test_withdraw(self):
        # create an application
        writer = LoanApplicationWriter(self.ipfsclient, "John", 1000)
        
        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.get_open_loan_applications()
        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].amount_asking, 1000)
        self.assertFalse(applications[0].closed)

        # withdraw it
        writer.withdraw_loan_application()
        
        # query it, check that it's not there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.get_open_loan_applications()
        self.assertEqual(len(applications), 0)

    def test_filter(self):
        # create 10 applications
        for i in range(10):
            LoanApplicationWriter(self.ipfsclient, "John", 1000 + i)

        # withdraw 3 of them
        for i in range(3):
            writer = LoanApplicationWriter(self.ipfsclient, "John", 1000 + i)
            writer.withdraw_loan_application()

        # confirm that there are 7 open applications
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.get_open_loan_applications()
        self.assertEqual(len(applications), 7)
        amounts = [app.amount_asking for app in applications]
        self.assertEqual(set(amounts), set(range(1003, 1011)))


if __name__ == '__main__':
    unittest.main()
