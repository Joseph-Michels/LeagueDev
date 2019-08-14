class UrlBuilder:
	"""
	Stores a url, potentially with one or more {parameter_name}s in it.
	When prompted, fills the {parameter_name}s out.
	"""
	def __init__(self, url:str, optionals=set()):
		self.url = url
		self.prompts = set()
		self.optionals = optionals
		last_idx = 0
		for _ in range(url.count("{")):
			open_idx, close_idx = url.find("{", last_idx), url.find("}", last_idx)
			self.prompts.add(url[open_idx+1:close_idx])
			last_idx = open_idx

	def prompt(self, **req_params_kargs):
		# assertions, handle optionals
		ending_dict = {}
		for inp_key in req_params_kargs:
			assert inp_key in self.prompts or inp_key in self.optionals, f"Unknown key {inp_key}"
			if inp_key in self.optionals:
				ending_dict[inp_key] = req_params_kargs[inp_key]
		for k in ending_dict:
			req_params_kargs.pop(k)

		end = '&'.join(f'{k}={v}' for k,v in ending_dict.items())

		# prompt for unentered
		for prompt in self.prompts:
			if prompt not in req_params_kargs:
				req_params_kargs[prompt] = input(f'    Enter "{prompt}": ')
		

		return self.url.format(**req_params_kargs) + ('' if end == '' else '?'+end)