import datetime
import streamlit as st
from utils import data, bcr


if __name__ == "__main__":

    # Streamlit page config & title
    title = "Spotify Timelapse Generator"
    st.set_page_config(
        page_title=title,
        page_icon=":headphones:",
        menu_items={"About": "https://github.com/D62/spotify-timelapse"},
    )
    st.title(title)

    # set max length for artist, album and track names
    max_length = 25

    if "video" not in st.session_state:
        st.session_state["video"] = ""

    # input form
    with st.form(key="Form"):
        uploaded_file = st.file_uploader("Upload Spotify zip file", type="zip")
        today = datetime.date.today()
        last_week = today - datetime.timedelta(days=7)
        start_date, end_date = st.date_input(
            "Date range",
            [last_week, today],
            min_value=datetime.date(2008, 10, 7),
            max_value=today,
        )
        chart_type = st.selectbox("Chart type", ("Artists", "Albums", "Tracks"))

        # launch functions after click on "Generate"

        if st.form_submit_button(label="Generate"):
            print("--- 🏁 start generating animation ---")
            progress_bar = st.progress(0)  # initialize progress bar

            with st.spinner("Fetching data..."):
                if uploaded_file is not None:
                    df = data.get_data(uploaded_file)
                    progress_bar.progress(1 / 3)

            with st.spinner("Preparing data frame..."):
                table = data.prepare_data(
                    df, chart_type, max_length, start_date, end_date
                )
                progress_bar.progress(2 / 3)

            with st.spinner("Creating animation... (this may take a while)"):
                title = f"Spotify streams by {chart_type.lower()}"
                st.session_state["video"] = bcr.create_bcr(title, max_length, table)
                progress_bar.progress(3 / 3)

            progress_bar.empty()

    if len(st.session_state["video"]) != 0:
        print("--- ✔️ animation generated successfully---")
        st.video(st.session_state["video"])  # display video in streamlit
        st.download_button(
            "Download",
            st.session_state["video"],
            f"spotify_{chart_type.lower()}_{start_date}_{end_date}.mp4",
        )  # download link
