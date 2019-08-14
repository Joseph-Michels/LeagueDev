class UrlBuilder:
	"""
	Stores a url, potentially with one or more {parameter_name}s in it.
	When prompted, fills the {parameter_name}s out.
	"""
	def __init__(self, url:str):
		self.url = url
		self.prompts = set()
		last_idx = 0
		for _ in range(url.count("{")):
			open_idx, close_idx = url.find("{", last_idx), url.find("}", last_idx)
			self.prompts.add(url[open_idx+1:close_idx])
			last_idx = open_idx

	def prompt(self, **req_params_kargs):
		for prompt in self.prompts:
			if prompt not in req_params_kargs:
				req_params_kargs[prompt] = input(f'    Enter "{prompt}": ')
		s = self.url.format(**req_params_kargs)
		return s