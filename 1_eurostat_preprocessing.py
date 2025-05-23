import geopandas as gpd
import pandas as pd
import csv
import numpy as np

data_dir = "./data"
output_dir = "./output"

# Add NUTS geom
geojson_file = "./data/NUTS_RG_01M_2024_3035.geojson"
gdf_nuts3 = gpd.read_file(geojson_file)


# Eurostat Data files
eurostat_data_files = [
    {
        "indicator": "income",
        "path": f"{data_dir}/estat_nama_10r_3gdp.tsv",
        "complete_year": "2017",
        "unit": "EUR_HAB"
    },
    {
        "indicator": "pop_density",
        "path": f"{data_dir}/estat_demo_r_d3dens.tsv",
        "complete_year": "2018",
        "unit": "PER_KM2",
        "nan": ":", # null value are ":" and not empty cell
    },
    {
        "indicator": "poverty",
        "path": f"{data_dir}/estat_ilc_peps11n.tsv",
        "complete_year": "2022",
        "unit": "PC",
        "nan": ":"
    },
    {
        "indicator": "age_index",
        "path": f"{data_dir}/estat_cens_21agr3.tsv",
        "complete_year": "2021",
        "unit": "NR"
    }
]

def get_average_country_indicator(name):
    try:
        average_country_indicator = int(merged_gdf[merged_gdf["CNTR_CODE"] == name]['data'].mean().round(0))
    except:
        average_country_indicator = np.nan
    return average_country_indicator

for eurostat_dict in eurostat_data_files:
    indicator = eurostat_dict["indicator"]
    path = eurostat_dict["path"]

    with open(path, "r") as file:
        lines = file.readlines()
    cleaned_lines = [line.replace(",", "\t") for line in lines]
    with open(eurostat_dict["path"].replace(data_dir, output_dir), "w") as cleaned_file:
        cleaned_file.writelines(cleaned_lines)
    
    df_eurostat = pd.read_csv(path.replace(data_dir, output_dir), sep="\t")
    df_eurostat.rename(columns={"geo\\TIME_PERIOD": "NUTS_ID"}, inplace=True)

    # Correct column name because there are space " " in name
    for col_year in range(2015, 2023):
        try:
            # remove unit in cell values: sometimes eurostat add € or p inside cells:
            df_eurostat[f'{col_year} '] = df_eurostat[f'{col_year} '].astype(str).str.extract(r'(\d+\.?\d*)')[0].astype(float)

            df_eurostat[f'{col_year}'] = pd.to_numeric(df_eurostat[f'{col_year} '], errors='coerce')
            df_eurostat.drop(columns=[f'{col_year} '], inplace=True)
        except:
            pass # no error on column name


    df_eurostat["data"] = df_eurostat[eurostat_dict["complete_year"]] 
    df_eurostat["data"] = df_eurostat["data"].replace(":", np.nan)
    df_eurostat = df_eurostat[df_eurostat['unit'] == eurostat_dict["unit"]]

    if indicator == "age_index": # compute ratio
        # df_eurostat = df_eurostat[df_eurostat["age"].isin(["Total", "Y_LT15", "Y65-84", "Y_GE85"])]
        df_eurostat = df_eurostat[df_eurostat["sex"] == "T"]
        df_Y_LT15 = df_eurostat[df_eurostat["age"] == "Y_LT15"].reset_index()
        df_Y_65_84 = df_eurostat[df_eurostat["age"] == "Y65-84"].reset_index()
        df_Y_GE85 = df_eurostat[df_eurostat["age"] == "Y_GE85"].reset_index()
        list_nuts_with_stat = list(df_Y_LT15["NUTS_ID"].values)
        df_total = df_eurostat[df_eurostat["age"] == "TOTAL"]
        df_total = df_total[df_total["NUTS_ID"].isin(list_nuts_with_stat)].reset_index()
        df_result = df_total[["NUTS_ID"]].reset_index()
        df_result["age_risk_percent"] = (df_Y_LT15["data"] + df_Y_65_84["data"] + df_Y_GE85["data"]) / df_total["data"] * 100
        df_eurostat = df_result
        df_eurostat["data"] = df_eurostat["age_risk_percent"]
        df_eurostat[eurostat_dict["complete_year"]] = df_eurostat["age_risk_percent"]
        df_eurostat["unit"] = "NR"


    print(indicator)
    print(df_eurostat[["NUTS_ID", "unit", "data", eurostat_dict["complete_year"]]])

    merged_gdf = gdf_nuts3.merge(df_eurostat, left_on="NUTS_ID", right_on="NUTS_ID", how="inner")
    df_country_level = merged_gdf[merged_gdf["LEVL_CODE"] == 0]
    df_country_level["average_country_indicator"] = merged_gdf["CNTR_CODE"].apply(get_average_country_indicator)
    df_country_level = df_country_level[["CNTR_CODE", "average_country_indicator"]]
    print(f"nb of countries: {len(df_country_level)}")
    merged_gdf = merged_gdf.merge(df_country_level, left_on="CNTR_CODE", right_on="CNTR_CODE", how="inner")
    merged_gdf[f"relative_{indicator}"] = merged_gdf[f"data"] - merged_gdf["average_country_indicator"]


    merged_gdf[["CNTR_CODE", "NUTS_NAME", "NUTS_ID", "LEVL_CODE", "unit", "data", eurostat_dict["complete_year"], "average_country_indicator", f"relative_{indicator}", "geometry"]].to_csv(f'./output/eurostat_{indicator}_{eurostat_dict["complete_year"]}.csv')