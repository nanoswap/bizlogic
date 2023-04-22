# Loan



::: bizlogic.loan.LoanStatus
    handler: python
    options:
      members:
        - loan_status
      show_root_heading: true
      show_source: true

::: bizlogic.loan.PaymentSchedule
    handler: python
    options:
      members:
        - create_payment_schedule
      show_root_heading: true
      show_source: true

::: bizlogic.loan.LoanWriter
    handler: python
    options:
      members:
        - __init__
        - _write
        - _generate_index
        - accept_terms
        - register_payment
      show_root_heading: true
      show_source: true


::: bizlogic.loan.LoanReader
    handler: python
    options:
      members:
        - __init__
        - query_for_status
        - query_for_borrower
        - query_for_lender
        - query_for_loan
      show_root_heading: true
      show_source: true
