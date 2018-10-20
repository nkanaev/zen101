compile:
	python3 compile.py

compile-gh:
	GITHUB=1 python3 compile.py

runlocal: compile
	(cd output && python3 -m http.server)

publish: compile-gh
	ghp-import output -m "$(shell date -u)" && git push git@github.com:nkanaev/zen101.git gh-pages:gh-pages -f
