app:
	pyinstaller --onefile --name todoist-converter --windowed app.py
debug:
	-rm -r dist/todoist-converter-debug.app
	-rm dist/todoist-converter-debug
	pyinstaller --onefile --name todoist-converter-debug --debug all --windowed app.py
	open dist/todoist-converter-debug 
test:
	nosetests
dev:
	pip install -r dev_requirements.pip
	python setup.py develop
install:
	python setup.py install
