from typing import Sequence

class TransactionException(Exception):
	def __init__(self, message: str, detail: Sequence[str]=[]):
		super().__init__(message)
		self.detail = detail
