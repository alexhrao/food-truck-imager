install:
	@rm -rf venv
	@python3 -m venv venv
	@chmod +x ./setup.sh
	@chmod +x ./runner.sh
	@source ./venv/bin/activate && pip3 install -r requirements.txt
