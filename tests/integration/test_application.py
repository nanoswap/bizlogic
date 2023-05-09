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
        for i in range(10):
            writer = LoanApplicationWriter(self.ipfsclient, "John", 1000 + i)
            writer.write()
            writers.append(writer)

        # withdraw 3 of them
        for writer in writers[:3]:
            writer2 = copy.deepcopy(writer)  # save to delete later
            writer2.withdraw_loan_application()
            writers.append(writer2)

        # confirm that there are 7 open applications
        reader = LoanApplicationReader(self.ipfsclient)
        applications = reader.get_open_loan_applications()

        print(applications)
        # the output doesn't have the closed field, or all of them are false
        #         [Store(index=<ipfskvs.index.Index object at 0x11d1ef310>, writer=None, reader=amount_asking: 1001
        # ), Store(index=<ipfskvs.index.Index object at 0x11d1eeb90>, writer=None, reader=amount_asking: 1006
        # ), Store(index=<ipfskvs.index.Index object at 0x11d206d90>, writer=None, reader=amount_asking: 1003
        # ), Store(index=<ipfskvs.index.Index object at 0x11d207950>, writer=None, reader=amount_asking: 1006
        # ), Store(index=<ipfskvs.index.Index object at 0x11d1ec2d0>, writer=None, reader=amount_asking: 1001
        # ), Store(index=<ipfskvs.index.Index object at 0x11d207fd0>, writer=None, reader=amount_asking: 1004
        # ), Store(index=<ipfskvs.index.Index object at 0x11d2053d0>, writer=None, reader=amount_asking: 1009
        # ), Store(index=<ipfskvs.index.Index object at 0x11d206850>, writer=None, reader=amount_asking: 1000
        # ), Store(index=<ipfskvs.index.Index object at 0x11d1efd90>, writer=None, reader=amount_asking: 1008
        # ), Store(index=<ipfskvs.index.Index object at 0x11d206610>, writer=None, reader=amount_asking: 1007
        # ), Store(index=<ipfskvs.index.Index object at 0x11d206010>, writer=None, reader=amount_asking: 1009
        # ), Store(index=<ipfskvs.index.Index object at 0x11d215610>, writer=None, reader=amount_asking: 1005
        # ), Store(index=<ipfskvs.index.Index object at 0x11d217810>, writer=None, reader=amount_asking: 1004
        # ), Store(index=<ipfskvs.index.Index object at 0x11d205cd0>, writer=None, reader=amount_asking: 1005
        # ), Store(index=<ipfskvs.index.Index object at 0x11d206090>, writer=None, reader=amount_asking: 1003
        # ), Store(index=<ipfskvs.index.Index object at 0x11d217f50>, writer=None, reader=amount_asking: 1000
        # ), Store(index=<ipfskvs.index.Index object at 0x11d216d10>, writer=None, reader=amount_asking: 1008
        # ), Store(index=<ipfskvs.index.Index object at 0x11d217e50>, writer=None, reader=amount_asking: 1002
        # ), Store(index=<ipfskvs.index.Index object at 0x11d1cbed0>, writer=None, reader=amount_asking: 1007
        # ), Store(index=<ipfskvs.index.Index object at 0x11d2150d0>, writer=None, reader=amount_asking: 1002
        # )]

        self.assertEqual(len(applications), 7)
        amounts = [app.amount_asking for app in applications]
        self.assertEqual(set(amounts), set(range(1003, 1011)))

        # delete them
        for writer in writers:
            writer.delete()
