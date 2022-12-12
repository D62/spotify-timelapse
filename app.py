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

    # file download explanation

    with st.expander("Click here for instructions to request your data from Spotify and get *my_spotify_data.zip*"):
        st.write("""In order to download your data from Spotify, you need to process as follow:""")
        st.write("""1) Open your Spotify privacy page: https://www.spotify.com/account/privacy/""")
        st.write("""2) Scroll down to the "Download your data" section""")
        st.image("https://raw.githubusercontent.com/D62/spotify-timelapse/main/images/step1.png")
        st.write("""3) Tick the box in the "Extended streaming history" panel""")
        st.write("""4) Press the "Request data" button""")
        st.write("""5) You will receive a link to confirm the request in your email, click on "Confirm" """)
        st.image("https://raw.githubusercontent.com/D62/spotify-timelapse/main/images/step2.png")
        st.write("""6) Wait until you receive your data (this can take up to 30 days)""")
        st.write("""7) Once your data is ready to download, you will get an email with a link to download *my_spotify_data.zip*""")
        st.image("https://raw.githubusercontent.com/D62/spotify-timelapse/main/images/step3.png")
        st.write("""You are now ready to upload *my_spotify_data.zip* in the form below.""")

    # set dummy min/max dates before file is uploaded
    max_date = datetime.date.today()
    min_date = max_date - datetime.timedelta(days=7)    

    # upload file
    disable_form = True
    uploaded_file = st.file_uploader("Upload *my_spotify_data.zip* (see above for instructions to request it)", type="zip")
    with st.spinner("Fetching data..."):
        if uploaded_file is not None:
            df = data.get_data(uploaded_file)
            if df is None:
                disable_form = True
                st.session_state["df"] = None
                st.error(f"Invalid file", icon="🚨")
            else:
                disable_form = False
                min_date, max_date = data.get_min_max_dates(df)
                st.session_state["df"] = df
                st.success(f"Spotify data successfully uploaded", icon="✔️")

    # input form
    with st.form(key="Form"):
        start_date, end_date = st.date_input(
            "Date range",
            [(max_date - datetime.timedelta(days=7)), max_date],
            min_value=min_date,
            max_value=max_date,
            disabled=disable_form
        )
        chart_type = st.selectbox("Chart type", ("Artists", "Albums", "Tracks"), disabled=disable_form)
        title = st.text_input("Animation title", f"My Spotify streams", max_chars=60, disabled=disable_form)

        # launch functions after click on "Generate"

        if st.form_submit_button(label="Generate", disabled=disable_form):
            print("--- 🏁 start generating animation ---")

            with st.spinner("Preparing data frame..."):
                table = data.prepare_data(
                    df, chart_type, max_length, start_date, end_date
                )

            with st.spinner("Creating animation... (this may take a while)"):
                st.session_state["video"] = bcr.create_bcr(title, max_length, table)

    if len(st.session_state["video"]) != 0:
        print("--- ✔️ animation generated successfully ---")
        st.video(st.session_state["video"])  # display video in streamlit
        st.download_button(
            "Download",
            st.session_state["video"],
            f"spotify_{chart_type.lower()}_{start_date}_{end_date}.mp4",
        )  # download link
