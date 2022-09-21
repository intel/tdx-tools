.DEFAULT_GOAL := wheel

wheel:
	pip3 install wheel --user
	python3 setup.py bdist_wheel

install:
	pip3 install dist/*.whl --force-reinstall -I --user

.PHONY: clean
clean:
	- rm -r dist
	- rm -r build/bdist.linux-x86_64/
	- rm -r src/*.egg-info/ 
	- rm -r *.egg-info
