import sys

def scrub(str):
	encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
	try:
		return str.encode(encoding)
	except UnicodeError:
		return str.encode('utf-8')

class KeyboardInterruptError(Exception): 
	'''Helper class for keyboard interupts'''
	pass		
		
class MethodProxy(object):
	'''Wraps a object & method for calling in a thread'''
	def __init__(self, obj, method):
		self.obj = obj
		if isinstance(method, basestring):
			self.methodName = method
		else:
			assert callable(method)
		self.methodName = method.func_name

	def __call__(self, *args, **kwargs):
		return getattr(self.obj, self.methodName)(*args, **kwargs)