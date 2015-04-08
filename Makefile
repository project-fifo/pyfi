LAST_VER=0.1.27
NEXT_VER=0.1.28
.phony: package clean

package:
	-rm doc/*~
	python setup.py sdist

clean:
	-find . -name __pycache__ -exec rm -r -- {} +
	-find . -name *.pyc -exec rm -r -- {} +

man:
	nroff -man doc/fifo.1 | less


rel:
	python setup.py bdist sdist upload -s

update-ver:
	for i in doc/*{1,5} setup.py bin/fifo; do sed -e 's/${LAST_VER}/${NEXT_VER}/' -i '' $$i; done
