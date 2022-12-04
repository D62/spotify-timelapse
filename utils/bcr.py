import bar_chart_race as bcr
import base64
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter


def create_bcr(title, max_length, table):

    plt.rcParams["font.family"] = "Helvetica, Arial"

    # initiate fig
    max_length = max_length / 115
    fig, ax = plt.subplots(figsize=(8, 4.5), facecolor="white", dpi=250)
    fig.subplots_adjust(left=max_length, bottom=-0.05, right=0.96, top=0.9)
    ax.margins(0, 0.01)

    # fix the size of the plot to the max value of the top item
    ax.set_xlim(0, table.max(numeric_only=True).max() + 0.5)

    ax.grid(which="major", axis="x", linestyle="-", linewidth=0.2, color="dimgrey")

    # ticks parameters
    ax.tick_params(axis="x", colors="dimgrey", labelsize=9, length=0)
    ax.tick_params(axis="y", colors="dimgrey", labelsize=9, length=0, direction="out")
    ax.xaxis.set_ticks_position("top")
    ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))

    # set borders colors
    for pos in ["top", "bottom", "right", "left"]:
        ax.spines[pos].set_edgecolor("white")

    # set title
    ax.set_title(title, fontsize=12, color="dimgrey")

    # bar chart race parameters
    html_str = bcr.bar_chart_race(
        table,
        n_bars=10,
        fig=fig,
        fixed_max=True,
        period_label={
            "x": 0.99,
            "y": 0.20,
            "ha": "right",
            "va": "center",
            "size": 36,
            "color": "#ccc",
            "family": "Tahoma",
            "weight": "bold",
        },
        period_summary_func=lambda v, r: {
            "x": 0.99,
            "y": 0.10,
            "s": f"Total: {v.sum():,.0f}",
            "ha": "right",
            "size": 18,
            "color": "#ccc",
            "family": "Tahoma",
            "weight": "bold",
        },
        steps_per_period=15,
        period_length=250,
    )

    # generate the video file
    start = html_str.find("base64,") + len("base64,")
    end = html_str.find('">')
    video = base64.b64decode(html_str[start:end])

    return video