class UrlBuilder:
	"""
	Stores a general url with any amount of undecided parameter names in brackets.
	This general url can build specific urls with decided arguments.
	Also supports optional parameters added to the end.
	"""

	def __init__(self, url:str, optional_param_names=set()):
		"""
		Initializes values, parsing required parameters from the url.
		For example, url="lol/summoner/v4/summoners/by-name/{summoner_name}" requires
		  a summoner_name to be specified when built.
		"""
		self.url = url
		self.prompts = set()
		self.optional_param_names = optional_param_names
		last_idx = 0
		for _ in range(url.count("{")):
			open_idx, close_idx = url.find("{", last_idx), url.find("}", last_idx)
			self.prompts.add(url[open_idx+1:close_idx])
			last_idx = open_idx


	def build(self, **req_params_kargs):
		"""
		Builds the general url into a specific one based off the passed kargs.
		Optional parameters are appended to the generic url like "?<param1>=<val1>&<param2>=<val2>".
		"""
		# assertions, handle optionals
		ending_dict = {}
		for inp_key in req_params_kargs:
			assert inp_key in self.prompts or inp_key in self.optional_param_names, f"Unknown key {inp_key}"
			if inp_key in self.optional_param_names:
				ending_dict[inp_key] = req_params_kargs[inp_key]
		for k in ending_dict:
			req_params_kargs.pop(k)

		end = '&'.join(f'{k}={v}' for k,v in ending_dict.items())

		# prompt for unentered
		for prompt in self.prompts:
			if prompt not in req_params_kargs:
				req_params_kargs[prompt] = input(f'    Enter "{prompt}": ')
		

		return self.url.format(**req_params_kargs) + ('' if end == '' else '?'+end)