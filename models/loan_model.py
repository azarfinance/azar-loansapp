class Loan:
    def __init__(self, client, amount):
        self.client = client
        self.amount = amount
        self.date = None
        self.status = 'pending'
        self.interest = amount * 0.1
        self.penalty = 0
