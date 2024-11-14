import streamlit as st
import polars as pl

st.write("Ciao skibidi tualet")

url = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/sdg_13_10?format=TSV&compressed=true"
data = (
    pl
    .read_csv(url, separator="\t")
    .select(
        pl.col("freq,airpol,src_crf,unit,geo\\TIME_PERIOD")
            .str.split(",")
            .list.to_struct(fields=["freq", "airpol",
                                "src_crf", "unit", "geo"])
            .alias("combined_info"),
        pl.col("*").exclude("freq,airpol,src_crf,unit,geo\\TIME_PERIOD")
    )
    .unnest("combined_info")
    .unpivot(index=["freq", "airpol", "src_crf", "unit", "geo"],
            value_name="emissions", 
            variable_name="year")
    .with_columns(
        year = pl.col("year").str.replace(" ", "").cast(pl.Int64),
        emissions = pl.col("emissions")
        .str.strip_chars_end(" bep")
        .cast(pl.Float64, strict=True)
    )
    .pivot(on="unit", values="emissions")
    .filter(pl.col("src_crf") == "TOTXMEMONIA")
)

st.write(data)

anno = st.selectbox("Seleziona anno", set(data.select("year").to_series().to_list()))

#data2 = data.filter(pl.col("year") == anno)
st.bar_chart(data, x="geo", y="T_HAB")

country = st.selectbox("Seleziona paese", set(data.select("geo").to_series().to_list()))

data2 = data.filter((pl.col("geo") == "IT") | (pl.col("geo") == "FR"))
st.line_chart(data2, x="year", y="T_HAB", color="geo")

anno_slider = st.slider("Ciao", min_value=1990, max_value=2022)
data2 = data.filter(pl.col("year") == anno_slider)
st.bar_chart(data2, x="geo", y="T_HAB")