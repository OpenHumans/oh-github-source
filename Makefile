.PHONY: local
local:
	@heroku local

.PHONY: pip
pip:
	@pipenv install --python 3.6 --dev

.PHONY: pipenv
pipenv:
	@pipenv shell

.PHONY: redis
redis:
	@docker run -p 6379:6379 -d redis