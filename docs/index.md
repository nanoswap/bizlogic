# Nanoswap Business Logic

[github.com/nanoswap/bizlogic](https://github.com/nanoswap/bizlogic)

# Installation

```
pip install bizlogic
```

# Usage

Here is the overall workflow. **Note**, this isn't how end users will actually interact with the platform. This will need to be deployed to a webserver with a UI for users to access. The private webserver deployment removes fraud opportunities. At time of writing there isn't functionality to create a sharable link to have someone you know vouch you - the names are just to make the workflow easier to understand.

Parameters and terminology:
 - **Adam** needs money, he is the "*borrower*"
 - **Eugene** is Adam's dad, and will cosign his application.
   - A "*vouch*" is a way to publicly approve of someone else's credit activity.
   - **Eugene** is the "*voucher*"
   - **Adam** is the "*vouchee*"
 - **Sarah** is Adam's rich Aunt, who will fund his loan. She is the "*lender*"

Process:
1. Adam creates a loan application

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.application import LoanApplicationWriter

    ipfsclient = Ipfs()
    amount_asking = 1000  # in raw XNO

    # Create a loan application and write the data to IPFS
    writer = LoanApplicationWriter(ipfsclient, <borrower_id>, amount_asking)
    print(writer.data)
```

2. Eugene vouches Adam

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.vouch import VouchWriter

    ipfsclient = Ipfs()

    # Create a vouch and write the data to IPFS
    VouchWriter(ipfsclient, <voucher_id>, <vouchee_id>)
```

3. Sarah searches for the loan application and vouches

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.application import LoanApplicationReader
    from bizlogic.vouch import VouchReader

    ipfsclient = Ipfs()

    reader = LoanApplicationReader(ipfsclient)

    reader = VouchReader(ipfsclient)
    vouches = reader.get_vouchees_for_borrower(<borrower_id>)
    print(vouches)
```

4. Sarah creates a loan offer for Adam

```py
    from ipfsclient.ipfs import Ipfs
    from bizlogic.loan import LoanWriter, PaymentSchedule
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


```

```py
    from bizlogic.loan import LoanReader

    # Someone else: Read the loan applications and write an offer
    reader = LoanApplicationReader(ipfsclient)

    # check your pending loan offers
    reader = LoanReader(ipfsclient)
    pending_offers = reader.get_open_loan_offers(borrower_id)
    print(pending_offers)

    # accept an offer

```
