
PYTHONPATH := $(CURDIR)
export PYTHONPATH

download_collection:
	python data_adapter/main.py $(collection)
