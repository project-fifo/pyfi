.phony: package clean

package:
	python setup.py sdist

clean:
	-find . -name __pycache__ -exec rm -r -- {} +
	-find . -name *.pyc -exec rm -r -- {} +

man:
	nroff -man doc/fifo.1 | less


rel:
	python setup.py bdist upload
