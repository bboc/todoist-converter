app:
	pyinstaller --onefile --log-level WARN --icon=icon.icns --name todoist-converter --windowed app.py
debug:
	-rm -r dist/todoist-converter-debug.app
	-rm dist/todoist-converter-debug
	pyinstaller --onefile --log-level WARN --icon=icon.icns --name todoist-converter-debug --debug all --windowed app.py
	open dist/todoist-converter-debug 
apptest:
	python app.py
test:
	nosetests
dev:
	pip install -r dev_requirements.pip
	python setup.py develop
install:
	python setup.py install
