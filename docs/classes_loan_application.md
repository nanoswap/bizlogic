# Loan Application

::: bizlogic.application.LoanApplicationWriter
    handler: python
    options:
      members:
        - __init__
        - _write
        - _generate_index
        - withdraw_loan_application
      show_root_heading: true
      show_source: true

::: bizlogic.application.LoanApplicationReader
    handler: python
    options:
      members:
        - __init__
        - get_open_loan_applications
      show_root_heading: true
      show_source: true
