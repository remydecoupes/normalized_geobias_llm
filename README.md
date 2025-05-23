# Geo-MISSED: Explore LLMs geographic bias for European Countries

The aim of this repository is to map geographic bias normalized by geo indicator.

Geo-MISSED aims to detect 2 LLMs behaviors when dealing with geographic information retrieval:

- Conservatism: Low error rate and, despite a low confidence
score, very little variation between responses to the same
prompt. This behavior is often observed in high-income
countries.
- Miscalibration: High error rate with high confidence scores
but too much variation between responses to the same prompt.
This is observed in low-income countries.

The pipeline is divided into 4 steps:

1. Preprocessing and extracting Eurostat data.
2. Running LLMs to predict the average income per inhabitant.
3. Displaying on maps the difference (**MAPE**) between the predicted income and Eurostat data.
4. Providing statistical indicators between models and geographic areas

See the maps: https://remydecoupes.github.io/Geo-MISSED/


## Data

| Title | link | metadata | name file |
|---|---|---|---|
| NUTS3 region| | | [NUTS_RG_01M_2024_3035.geojson](./data/NUTS_RG_01M_2024_3035.geojson)|
| capitals of all the world | [link](https://ec.europa.eu/eurostat/web/gisco/geodata/administrative-units/countries) | - | CNTR_RG_20M_2024_3035.geojson |
| Eurostat GDP at current market prices by NUTS 3 regions| [link](https://ec.europa.eu/eurostat/web/main/data/database) | [metadata](https://ec.europa.eu/eurostat/cache/metadata/en/reg_eco10_esms.htm) | [estat_nama_10r_3gdp.tsv](./data/estat_nama_10r_3gdp.tsv) |
| Eurostat population density| [link](https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/demo_r_d3dens/?format=TSV&compressed=true) | - | estat_demo_r_d3dens.tsv | 
| Eurostat Persons at risk of poverty or social exclusion by NUTS region  | [link](https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/ilc_peps11n/?format=TSV&compressed=true) |  | estat_ilc_peps11n.tsv |
| Eurostat Population by broad age group and NUTS 3 region  | [link](https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/cens_21agr3/?format=TSV&compressed=true) |  | estat_cens_21agr3.tsv |

## Install environment

**Code**:

```bash
conda create -n geobias python=3.10 pip ipython
conda activate geobias 
pip install geopandas pandas folium langchain langchain_community langchain_core timeout_decorator langchain_openai matplotlib pycountry torch transformers datasets seaborn
pip install 'accelerate>=0.26.0'
pip install -U bitsandbytes
```

**Data**: 

You have to donwload the data files into data folder

**Reproduce the study**:
```bash
# Eurostat data pre-processing
python 1_eurostat_preprocessing.py

# Inferring with LLMs
chmod u+x 2_run_all_transformers_models.sh
./2_run_all_transformers_models.sh

# Compute error and normalized error
chmod u+X 3_run_all_transformers_models.sh
./3_run_all_transformers_models.sh

# post-processing the results with jupyter or jupyter-lab:
4_synthized_results.ipynb
```
-------
## Some visualisation from this repository

| Bar Plot Error with range of prediction                       | Scatter Plot: Confidence vs Error                  | Bivariate Map                                  |
|--------------------------------------------------------|---------------------------------------------------|------------------------------------------------|
| ![](figs/barplot_error_with_deviation.png)             | ![](figs/scatter_plot_global_picture.png)         | ![](figs/bivariate_llama-70B_poverty.png)      |


-------
<img align="left" src="https://www.umr-tetis.fr/images/logo-header-tetis.png">


|           |
|----------------------|
| Rémy Decoupes        |