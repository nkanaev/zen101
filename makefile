compile:
	python3 compile.py

publish: compile
	ghp-import output -m "$(shell date -u)" && git push git@github.com:nkanaev/zen101.git gh-pages:gh-pages -f
