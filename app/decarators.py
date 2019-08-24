from functools import wraps

class OneOfAKeyAtATime:
	lock_dict = {}

	def __init__(self, key):
		self.key = key
		if key not in OneOfAKeyAtATime.lock_dict:
			self._unlock()
		
	def _unlock(self):
		OneOfAKeyAtATime.lock_dict[self.key] = False
	def _lock(self):
		OneOfAKeyAtATime.lock_dict[self.key] = True
	def is_locked(self):
		return OneOfAKeyAtATime.lock_dict[self.key]

	def __call__(self, fxn):
		@wraps(fxn)
		def wrapper_function(*args, **kargs):
			while True:
				if not self.is_locked():
					self._lock()
					val = fxn(*args, **kargs)
					self._unlock()
					return val
		return wrapper_function