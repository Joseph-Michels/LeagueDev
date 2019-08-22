class UrlBuilder:
	"""
	Stores a general url with any amount of undecided parameter names in brackets.
	This general url can build specific urls with decided arguments.
	Also supports optional parameters added to the end.
	"""

	def __init__(self, url:str):
		"""
		Initializes attributes.
		When url="lol/summoner/v4/summoners/by-name/{summoner_name}" is built,
		  a summoner_name=<something> needs to be specified in kargs when built.
		"""
		self.url = url
		self.prompts = set()
		last_idx = 0
		for _ in range(url.count("{")):
			open_idx, close_idx = url.find("{", last_idx), url.find("}", last_idx)
			self.prompts.add(url[open_idx+1:close_idx])
			last_idx = open_idx


	def build(self, **req_params_kargs):
		"""
		Builds the general url into a specific one based off the passed kargs.
		Extra parameters are appended to the generic url like "?<param1>=<val1>&<param2>=<val2>".
		"""

		end = '&'.join(f'{key}={{{key}}}' for key in req_params_kargs if key not in self.prompts)

		return (self.url + ('' if end=='' else '?'+end)).format(**req_params_kargs)