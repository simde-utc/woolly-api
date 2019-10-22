class TransactionException(Exception):
	def __init__(self, message, detail=None):
		super().__init__(message)
		self.detail = detail
