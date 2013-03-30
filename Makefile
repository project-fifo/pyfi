.phony: package clean

package:
	python setup.py sdist

clean:
	-find . -name __pycache__ -exec rm -r -- {} +
