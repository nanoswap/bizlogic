import unittest
from unittest.mock import MagicMock
from ipfsclient.ipfs import Ipfs
from bizlogic.application import LoanApplicationWriter, LoanApplicationReader


class TestApplication(unittest.TestCase):
    
    def setUp(self):
        self.ipfsclient = Ipfs()

    def test_read_write(self):
        # create an application
        mock_store = MagicMock(return_value=None)
        writer = LoanApplicationWriter(self.ipfsclient, "John", 1000)
        with unittest.mock.patch('ipfskvs.store.Store.add', mock_store):
            writer.write()
        
        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        # mock the reader to read the application
        mock_store = MagicMock(return_value=[writer.data])
        with unittest.mock.patch('ipfskvs.store.Store.query', mock_store):
            applications = reader.get_open_loan_applications()

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].amount_asking, 1000)
        self.assertFalse(applications[0].closed)

    def test_withdraw(self):
        # create an application
        mock_store = MagicMock(return_value=None)
        writer = LoanApplicationWriter(self.ipfsclient, "John", 1000)
        with unittest.mock.patch('ipfskvs.store.Store.add', mock_store):
            writer.write()
        
        # query it, check that it's there
        reader = LoanApplicationReader(self.ipfsclient)
        # mock the reader to read the application
        mock_store = MagicMock(return_value=[writer.data])
        with unittest.mock.patch('ipfskvs.store.Store.query', mock_store):
            applications = reader.get_open_loan_applications()

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].amount_asking, 1000)
        self.assertFalse(applications[0].closed)

        # withdraw it
        with unittest.mock.patch('ipfskvs.store.Store.add', mock_store):
            writer.withdraw_loan_application()

        # query it, check that it's not there
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.get_open_loan_applications()
        self.assertEqual(len(applications), 0)

    def test_filter(self):
        mock_store = MagicMock(return_value=None)

        # create 10 applications
        for i in range(10):
            writer = LoanApplicationWriter(self.ipfsclient, "John", 1000 + i)
            with unittest.mock.patch('ipfskvs.store.Store.add', mock_store):
                writer.write()

        # withdraw 3 of them
        for i in range(3):
            writer = LoanApplicationWriter(self.ipfsclient, "John", 1000 + i)
            with unittest.mock.patch('ipfskvs.store.Store.add', mock_store):
                writer.withdraw_loan_application()

        # confirm that there are 7 open applications
        reader = LoanApplicationReader(self.ipfsclient)
        mock_store = MagicMock(return_value=[writer.data])
        with unittest.mock.patch('ipfskvs.store.Store.query', mock_store):
            applications = reader.get_open_loan_applications()

        self.assertEqual(len(applications), 7)
        amounts = [app.amount_asking for app in applications]
        self.assertEqual(set(amounts), set(range(1003, 1011)))
