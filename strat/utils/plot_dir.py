import seaborn as sns

sns.set_theme(style="whitegrid")
import pandas as pd
import plotly.graph_objs as go
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot


def sns_cat(df: pd.DataFrame, x: str, y: str, hue: str):
    sns.catplot(
        data=df, kind="bar", x=x, y=y, hue=hue, palette="dark", alpha=0.6, height=6
    )


def plot_allocation_reward_sankey(df_nodes, df_links, LP_addr_label):
    data_trace = dict(
        type="sankey",
        arrangement="snap",
        domain=dict(x=[0, 1], y=[0, 1]),
        orientation="h",
        valueformat=".1f",
        node=dict(
            pad=10,
            # thickness = 30,
            line=dict(color="black", width=0),
            label=df_nodes["Label"].dropna(axis=0, how="any"),
            color=df_nodes["Color"],
        ),
        link=dict(
            source=df_links["Source"],  # .dropna(axis=0, how='any'),
            target=df_links["Target"],  # .dropna(axis=0, how='any'),
            value=df_links["Value"],  # .dropna(axis=0, how='any'),
            color=df_links["Link Color"].dropna(axis=0, how="any"),
        ),
    )

    layout = dict(
        title=f"{LP_addr_label} allocations and reward sources",
        height=350,
        font=dict(size=10),
    )

    fig = dict(data=[data_trace], layout=layout)
    iplot(fig, validate=False)
    # fig.show("svg")


def plot_allocation_reward_sankey_2(df_nodes, df_links, LP_addr_label):
    fig = go.Figure(
        data=[
            go.Sankey(
                valueformat=".0f",
                valuesuffix="TWh",
                # Define nodes
                node=dict(
                    pad=15,
                    thickness=15,
                    line=dict(color="black", width=0.5),
                    label=df_nodes["Label"].dropna(axis=0, how="any"),
                    color=df_nodes["Color"],
                ),
                # Add links
                link=dict(
                    source=df_links["Source"],  # .dropna(axis=0, how='any'),
                    target=df_links["Target"],  # .dropna(axis=0, how='any'),
                    value=df_links["Value"],  # .dropna(axis=0, how='any'),
                    color=df_links["Link Color"].dropna(axis=0, how="any"),
                ),
            )
        ]
    )

    fig.update_layout(
        title_text=f"{LP_addr_label} allocations and reward sources", font_size=10
    )
    fig.show("svg")
