compile:
	python compile.py

compile-gh:
	GITHUB=1 python compile.py

runlocal: compile
	(cd output && python -m SimpleHTTPServer)

publish: compile-gh
	ghp-import output && git push git@github.com:nkanaev/zen101.git gh-pages:gh-pages
