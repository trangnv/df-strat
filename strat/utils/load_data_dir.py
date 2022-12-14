import pandas as pd
from glob import glob
from enforce_typing import enforce_types
import requests

data_dir = "mydata"


def load_ve_balances():
    ve_balances = pd.DataFrame(
        columns=[
            "LP_addr",
            "balance",
            "perc",
            "round",
        ]
    )
    for dir_path in glob(f"{data_dir}/*/", recursive=False):
        file_path = dir_path + "/vebals.csv"
        df = pd.read_csv(file_path)

        r = int(dir_path[:-1][9:])
        df["round"] = r

        total_ve = df["balance"].sum()
        df["perc"] = df["balance"] / total_ve * 100

        # df["LP_addr_short"] = df["LP_addr"].str[:5] + "..." + df["LP_addr"].str[-3:]
        ve_balances = ve_balances.append(df, ignore_index=True)
    ve_balances = ve_balances.sort_values(
        ["round", "balance"], ascending=[True, True]
    ).reset_index(drop=True)
    return ve_balances


def load_ve_allocations_pct():
    ve_allocations_pct = pd.DataFrame(
        columns=[
            "chainID",
            "nft_addr",
            "LP_addr",
            "percent",
            "round",
        ]
    )

    for dir_path in glob(f"{data_dir}/*/", recursive=False):
        file_path = dir_path + "/allocations.csv"
        df = pd.read_csv(file_path)

        r = int(dir_path[:-1][9:])
        df["round"] = r

        ve_allocations_pct = ve_allocations_pct.append(df, ignore_index=True)
    ve_allocations_pct = ve_allocations_pct.sort_values(
        ["round"], ascending=[True]
    ).reset_index(drop=True)
    return ve_allocations_pct


def cal_ve_allocations(ve_balances, ve_allocations_pct, wallet_dict):
    ve_allocations = pd.merge(
        ve_balances, ve_allocations_pct, on=["LP_addr", "round"], how="left"
    ).reset_index(
        drop=True
    )  # .fillna('')
    ve_allocations["allocation"] = ve_allocations["balance"] * ve_allocations["percent"]
    ve_allocations["LP_addr_label"] = ve_allocations["LP_addr"].map(wallet_dict)
    ve_allocations["LP_addr_label"] = ve_allocations["LP_addr_label"].fillna(
        value="unknown"
    )
    return ve_allocations


def load_lp_rewards():
    lp_rewards = pd.DataFrame(
        columns=["chainID", "LP_addr", "OCEAN_amt", "reward_perc_per_LP", "round"]
    )
    total_rewards = _get_total_rewards()
    for dir_path in glob(f"{data_dir}/*/", recursive=False):
        file_path = dir_path + "/rewardsperlp-OCEAN.csv"
        df = pd.read_csv(file_path)

        r = int(dir_path[:-1][9:])
        df["round"] = r
        df = df.sort_values("OCEAN_amt", ascending=False).reset_index(drop=True)

        df["reward_perc_per_LP"] = df["OCEAN_amt"] / total_rewards[r] * 100
        df["round"] = r
        lp_rewards = lp_rewards.append(df, ignore_index=True)

        lp_rewards.loc[(lp_rewards["reward_perc_per_LP"] >= 5)]
    lp_rewards = lp_rewards.sort_values(["round"], ascending=[True]).reset_index(
        drop=True
    )
    return lp_rewards


def load_nft_rewards():
    nft_rewards = pd.DataFrame(
        columns=[
            "nft",
            "reward_amount",
            "reward_perc",
            "round",
        ]
    )
    # chainID,nft_addr,LP_addr,amt,token

    total_rewards = {}
    for dir_path in glob(f"{data_dir}/*/", recursive=False):
        file_path = dir_path + "/rewardsinfo-OCEAN.csv"
        r = int(dir_path[:-1][9:])
        df = pd.read_csv(file_path)

        x = []
        y = []
        for nft_addr in df["nft_addr"].unique():
            x.append(nft_addr)
            amt = df[df["nft_addr"] == nft_addr]["amt"].sum()
            y.append(amt)

        total_reward = sum(y)
        total_rewards[r] = total_reward

        nft_reward = pd.DataFrame(
            {
                "nft": x,
                "reward_amount": y,
                # "reward_perc": y / total_reward * 100,
                "reward_perc": [y1 / total_reward * 100 for y1 in y],
                "round": r,
            }
        )
        # df["reward_perc_per_LP"] = df["OCEAN_amt"] / total_rewards[r] * 100
        nft_rewards = nft_rewards.append(nft_reward, ignore_index=True)
        # print(f'Total reward in round {r} is: {total_reward} Ocean' )
    nft_rewards = nft_rewards.sort_values(["round"], ascending=[True]).reset_index(
        drop=True
    )

    return nft_rewards


def load_nft_lp_rewards(wallet_dict):
    nft_lp_rewards = pd.DataFrame(
        columns=[
            "chainID",
            "nft_addr",
            "LP_addr",
            "amt",
            "token",
            "round",
            "LP_addr_label",
        ]
    )
    for dir_path in glob(f"{data_dir}/*/", recursive=False):
        file_path = dir_path + "/rewardsinfo-OCEAN.csv"
        df = pd.read_csv(file_path)

        r = int(dir_path[:-1][9:])
        df["round"] = r
        nft_lp_rewards = nft_lp_rewards.append(df, ignore_index=True)
    nft_lp_rewards["LP_addr_label"] = nft_lp_rewards["LP_addr"].map(wallet_dict)
    return nft_lp_rewards


def load_nft_vol():
    nft_vols = pd.DataFrame(
        columns=["chainID", "basetoken_addr", "nft_addr", "vol_amt", "round"]
    )
    for dir_path in glob(f"{data_dir}/*/", recursive=False):
        for chainID in _CHAINID_TO_NETWORK.keys():
            try:
                file_path = f"{dir_path}nftvols-{chainID}.csv"
                r = int(dir_path[:-1][9:])
                df = pd.read_csv(file_path)
                df["round"] = r
                nft_vols = nft_vols.append(df, ignore_index=True)
            except:
                continue
    nft_vols = nft_vols.sort_values(["round"], ascending=[True]).reset_index(drop=True)
    return nft_vols


def _get_total_rewards():
    # nft_rewards = pd.DataFrame(columns=["nft", "reward_amount", "reward_perc", "round"])
    total_rewards = {}
    for dir_path in glob(f"{data_dir}/*/", recursive=False):
        file_path = dir_path + "/rewardsinfo-OCEAN.csv"
        r = int(dir_path[:-1][9:])
        df = pd.read_csv(file_path)

        x = []
        y = []
        for nft_addr in df["nft_addr"].unique():
            x.append(nft_addr)
            amt = df[df["nft_addr"] == nft_addr]["amt"].sum()
            y.append(amt)

        total_reward = sum(y)
        total_rewards[r] = total_reward

        # nft_reward = pd.DataFrame({'nft':x, 'reward_amount':y, 'reward_perc': y/total_reward*100, 'round': r})
        # nft_rewards = nft_rewards.append(nft_reward, ignore_index=True)
        # print(f'Total reward in round {r} is: {total_reward} Ocean' )

    return total_rewards


_CHAINID_TO_NETWORK = {
    8996: "development",  # ganache
    1: "mainnet",
    3: "ropsten",
    4: "rinkeby",
    56: "bsc",
    137: "polygon",
    246: "energyweb",
    1287: "moonbase",
    1285: "moonriver",
    80001: "mumbai",
}


@enforce_types
def chainIdToNetwork(chainID: int) -> str:
    """Returns the network name for a given chainID"""
    return _CHAINID_TO_NETWORK[chainID]


@enforce_types
def chainIdToSubgraphUri(chainID: int) -> str:
    """Returns the subgraph URI for a given chainID"""
    sg = "/subgraphs/name/oceanprotocol/ocean-subgraph"
    # if chainID == DEV_CHAINID:
    #     return "http://127.0.0.1:9000" + sg

    network_str = chainIdToNetwork(chainID)
    return f"https://v4.subgraph.{network_str}.oceanprotocol.com" + sg


def submitQuery(query: str, chainID: int) -> dict:
    subgraph_url = chainIdToSubgraphUri(chainID)
    request = requests.post(subgraph_url, "", json={"query": query})
    if request.status_code != 200:
        raise Exception(f"Query failed. Return code is {request.status_code}\n{query}")

    result = request.json()

    return result


#   orders(where: {datatoken_: {nft: "0xaa8af64ee67bc318d513a6562f096db7fcd5233b"}}) {


def query_nft_orders(nft_addr, chainID):
    query = """
{
  orders(where: 
    {
      datatoken_: {nft: %s
      }
    }) {
    block
    datatoken {
      id
      name
      lastPriceToken {
        id
      }
      lastPriceValue
      nft {
        owner {
          id
        }
      }
    }
    amount
    consumer {
      id
    }
  }
}
        """ % (
        nft_addr
    )
    result = submitQuery(query, chainID)
    orders = pd.json_normalize(result["data"]["orders"])
    return orders


#     {
#   nfts(where: { owner_: {id: "0x52b4943bae9cbda94f5f7e8b87a038bc96533a33"}}) {
#     owner {
#       id
#     }
#     address
#   }
# }
