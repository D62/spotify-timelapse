import json
import pandas as pd
import streamlit as st
import zipfile


def get_data(uploaded_file):
    df = None
    with zipfile.ZipFile(uploaded_file, "r") as z:
        for filename in z.namelist():
            if filename.split(".")[0][:-1] == "MyData/endsong_":
                with z.open(filename) as f:
                    json_load = json.load(f)
                    json_normalized = pd.json_normalize(
                        json_load,
                        errors="ignore",
                    )
                df = pd.concat([df, json_normalized])
    df = df.reset_index(drop=True)
    return df


def prepare_data(df, chart_type, max_length, start_date, end_date):

    # convert ISO-8601 format to date only
    df["date"] = pd.to_datetime(df["ts"]).dt.tz_convert(None)
    df["date"] = df["date"].dt.date

    # limit dataframe to selected dates
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]

    # remove rows when artist, album, or track names are empty
    df = df.dropna(
        subset=[
            "master_metadata_album_artist_name",
            "master_metadata_album_album_name",
            "master_metadata_track_name",
        ]
    )

    df["master_metadata_album_artist_name"] = df[
        "master_metadata_album_artist_name"
    ].apply(
        lambda x: " ".join(x[:max_length].split(" ")[:-1]) + "..."
        if len(x) > max_length
        else x
    )

    # merge into one column artist, album and track names
    if chart_type == "Artists":
        df["content"] = df["master_metadata_album_artist_name"]
    elif chart_type == "Albums":
        df["master_metadata_album_album_name"] = df[
            "master_metadata_album_album_name"
        ].apply(
            lambda x: " ".join(x[:max_length].split(" ")[:-1]) + "..."
            if len(x) > max_length
            else x
        )
        df["content"] = df[
            ["master_metadata_album_artist_name", "master_metadata_album_album_name"]
        ].agg("\n".join, axis=1)
    elif chart_type == "Tracks":
        df["master_metadata_track_name"] = df["master_metadata_track_name"].apply(
            lambda x: " ".join(x[:max_length].split(" ")[:-1]) + "..."
            if len(x) > max_length
            else x
        )
        df["content"] = df[
            ["master_metadata_album_artist_name", "master_metadata_track_name"]
        ].agg("\n".join, axis=1)

    # remove all unnecessary columns
    df = df[["ts", "date", "content"]]

    # get min and max dates
    min_date = df["date"].min()
    max_date = df["date"].max()

    # pivot data frame
    table = pd.pivot_table(
        df,
        values="ts",
        index=["date"],
        columns=["content"],
        aggfunc="count",
        fill_value=0,
    )

    # fill empty dates
    idx = pd.date_range(min_date, max_date)
    table = table.reindex(idx, fill_value=0)

    # cumulate daily scrobbles
    table = table.cumsum(axis=0)

    return table
