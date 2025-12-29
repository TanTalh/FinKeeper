from matplotlib.figure import Figure

def build_pie_chart(labels, values, colors):
    fig = Figure(figsize=(5.5, 5.5), dpi=100)
    ax = fig.add_axes([0.0, 0.0, 0.78, 1.0])

    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    wedges, _ , autotext = ax.pie(
        values,
        labels=None,
        colors=colors,
        startangle=90,
        autopct="%1.1f%%",
        pctdistance=0.75
    )

    ax.set_aspect("equal")

    ax.legend(
        wedges,
        labels,
        loc="upper left",
        bbox_to_anchor=(1.02, 0.9),
        frameon=False
    )

    return fig