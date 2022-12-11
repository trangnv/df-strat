import pandas as pd
from glob import glob


def load_nodes_and_links(ve_allocations, nft_lp_reward, LP_addr_label: str, _round):
    _alloc = ve_allocations.loc[
        (ve_allocations["round"] == _round)
        & (ve_allocations["LP_addr_label"] == LP_addr_label)
        & (ve_allocations["allocation"] > 0)
    ]
    _reward = nft_lp_reward.loc[
        (nft_lp_reward["round"] == _round)
        & (nft_lp_reward["LP_addr_label"] == LP_addr_label)
    ]
    last_node_id = _alloc["nft_addr"].shape[0] + 1
    nodes = [["ID", "Label", "Color"], [0, f"{LP_addr_label}", "#3182bd"]]
    links = [["Source", "Target", "Value", "Link Color"]]

    for i, nft_addr in enumerate(_alloc["nft_addr"]):
        nft_addr_short = f"{nft_addr[:5]}"
        node = [i + 1, nft_addr_short, "#9ecae1"]
        nodes.append(node)

        _alloc_ = (
            _alloc.loc[_alloc["nft_addr"] == nft_addr, "allocation"].values[0] / 100
        )
        links.append([0, i + 1, _alloc_, "#deebf7"])

        try:
            _reward_ = _reward.loc[_reward["nft_addr"] == nft_addr, "amt"].values[0]
            links.append([i + 1, last_node_id, _reward_, "#e5f5e0"])
        except:
            continue
    nodes.append([last_node_id, "reward", "#31a354"])

    nodes_headers = nodes.pop(0)
    links_headers = links.pop(0)
    df_nodes = pd.DataFrame(nodes, columns=nodes_headers)
    df_links = pd.DataFrame(links, columns=links_headers)

    return df_nodes, df_links
