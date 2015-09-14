compile: 
	python compile.py

runlocal:
	(cd output && python -m SimpleHTTPServer)

publish: compile
	ghp-import output && git push git@github.com:nkanaev/nkanaev.github.io.git gh-pages:gh-pages
