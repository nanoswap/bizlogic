# Nanoswap Business Logic

[github.com/nanoswap/bizlogic](https://github.com/nanoswap/bizlogic)

# Installation

```
pip install bizlogic
```

# Usage

Here is the overall workflow. **Note**, this isn't how end users will actually interact with the platform. This will need to be deployed to a webserver with a UI for users to access. The private webserver deployment removes fraud opportunities. At time of writing there isn't functionality to create a sharable link to have someone you know "vouch" you - the names are just to make the workflow easier to understand.

Parameters and terminology:  
 - **Adam** needs money, he is the "*borrower*"  
 - **Eugene** is Adam's dad, and will cosign his application.  
   - A "*vouch*" is a way to publicly approve of someone else's credit activity.  
   - **Eugene** is the "*voucher*"  
   - **Adam** is the "*vouchee*"  
 - **Sarah** is Adam's rich Aunt, who will fund his loan. She is the "*lender*"  

Process:  

1. Adam creates a loan application.

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.application import LoanApplicationWriter

    ipfsclient = Ipfs()
    amount_asking = 1000  # in raw XNO

    # Create a loan application and write the data to IPFS
    writer = LoanApplicationWriter(ipfsclient, <borrower_id>, amount_asking)
    writer.write()
```

2. Eugene vouches Adam

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.vouch import VouchWriter

    ipfsclient = Ipfs()

    # Create a vouch and write the data to IPFS
    writer = VouchWriter(ipfsclient, <voucher_id>, <vouchee_id>)
    writer.write()
```

3. Sarah searches for the loan application and vouches. Bizlogic does not cover credit checks, that will be a separate package.

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.application import LoanApplicationReader
    from bizlogic.vouch import VouchReader

    ipfsclient = Ipfs()

    # search for applications (Adam's request for 1000 raw XNO)
    reader = LoanApplicationReader(ipfsclient)
    applications = reader.get_open_loan_applications()
    print(applications)

    # parse borrower from applications
    ...

    # search for vouchees (Eugene's id will be in the response data)
    reader = VouchReader(ipfsclient)
    vouchees = reader.get_vouchees_for_borrower(<borrower_id>)
    print(vouches)

    # search for vouchers (the people Adam vouched for)
    vouchers = reader.get_vouchers_for_borrower(<borrower_id>)
    print(vouchers)
```

4. Sarah creates a loan offer for Adam.

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.loan.writer import LoanWriter
    from bizlogic.loan.repayment import PaymentSchedule
    import datetime

    ipfsclient = Ipfs()
    expiry = datetime.datetime.now() + datetime.timedelta(days=30)
    repayment_schedule = PaymentSchedule.create_payment_schedule(
        amount=1000,  # in raw XNO
        interest_rate=1.05,  # 5%
        total_duration=datetime.timedelta(days=100),
        number_of_payments=10
    )

    # Create the loan offer and write it to IPFS
    writer = LoanWriter(
        <borrower_id>,
        <lender_id>,
        1000,
        repayment_schedule,
        expiry  # the time the borrower has to accept the offer
    )
    writer.write()
```

5. Adam views his loan offers and accepts the offer.

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.loan.reader import LoanReader

    ipfsclient = Ipfs()

    # List open loan offers
    reader = LoanReader(ipfsclient)
    offers = reader.get_open_loan_offers(<borrower_id>)
    print(offers)

    # Parse the loan_data and loan_id from the offers result
    loan_data = ...
    loan_id = ...

    # Accept the offer they select
    writer = LoanWriter.from_data(ipfsclient, loan_data)
    writer.accept_terms()
    writer.write()
```

6. Adam gets his active loans and makes a payment

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.loan.reader import LoanReader
    from bizlogic.loan.writer import LoanWriter

    ipfsclient = Ipfs()

    # read loans
    reader = LoanReader()
    loans = reader.query_for_borrower(<borrower_id>)
    print(loans)

    # make the XNO payment
    transaction_id = ...

    # register the payment
    writer = LoanWriter()
```
