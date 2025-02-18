# Data Adapter
General data adapter that provides functionalities for other data adapters.

## Installation

To install data_adapter, follow these steps:

* git-clone data_adapter into local folder:
  `https://github.com/sedos-project/data_adapter.git`
* enter folder `cd data_adapter`
* create virtual environment using conda: `conda env create -f environment.yml`
* activate environment: `conda activate data_adapter`
* install data_adapter_oemof package using poetry, via: `poetry install`

## Functionalities

* Download of the latest data and metadata
* Verification checks on the downloaded data and metadata
* Preprocessing of the process data such as:
  * Merging, filtering and transforming 
  * Unit conversion
