
compile:
	slice2py slices/*.ice --output-dir ./icemongo/Base -IDIR=./slices; \
	mv -f ./icemongo/Base/Base/*.py ./icemongo/Base/; \
    rm -r ./icemongo/Base/Base;

compileSimple:
	slice2py examples/simple/*.ice -I ./slices

develop:
	python setup.py  develop


