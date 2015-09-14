compile: 
	python compile.py

runlocal:
	(cd output && python -m SimpleHTTPServer)

publish: compile
	ghp-import output && git push git@github.com:nkanaev/zen101.git gh-pages:gh-pages
