import pandas as pd
from enforce_typing import enforce_types
import requests
from datetime import datetime

# data_dir = "mydata"


def load_ve_balance(dir_path):

    file_path = dir_path + "/vebals.csv"
    df = pd.read_csv(file_path)

    # week = int(dir_path[31:33])
    today = datetime.now()
    week = today.strftime("%W")
    df["week"] = week

    total_ve = df["balance"].sum()
    df["perc"] = df["balance"] / total_ve * 100

    # ve_balance = ve_balance.append(df, ignore_index=True)

    df = df.sort_values(["balance"], ascending=[True]).reset_index(drop=True)
    return df


def load_ve_allocation_pct(dir_path):
    # ve_allocation_pct = pd.DataFrame(
    #     columns=[
    #         "chainID",
    #         "nft_addr",
    #         "LP_addr",
    #         "percent",
    #         "week",
    #     ]
    # )

    file_path = dir_path + "/allocations.csv"
    df = pd.read_csv(file_path)

    # week = int(dir_path[31:33])
    today = datetime.now()
    week = today.strftime("%W")
    df["week"] = week

    # ve_allocation_pct = ve_allocation_pct.sort_values(
    #     ["week"], ascending=[True]
    # ).reset_index(drop=True)
    return df


def cal_ve_allocation(ve_balance, ve_allocation_pct, wallet_dict):
    ve_allocation = pd.merge(
        ve_balance, ve_allocation_pct, on=["LP_addr", "week"], how="left"
    ).reset_index(
        drop=True
    )  # .fillna('')
    ve_allocation["allocation"] = ve_allocation["balance"] * ve_allocation["percent"]
    ve_allocation["LP_addr_label"] = ve_allocation["LP_addr"].map(wallet_dict)
    ve_allocation["LP_addr_label"] = ve_allocation["LP_addr_label"].fillna(
        value="unknown"
    )
    ve_allocation = ve_allocation.sort_values(
        ["allocation"], ascending=[False]
    ).reset_index(drop=True)
    return ve_allocation


def load_lp_reward(dir_path, wallet_dict):
    # lp_reward = pd.DataFrame(
    #     columns=["chainID", "LP_addr", "OCEAN_amt", "reward_perc_per_LP", "week"]
    # )
    total_reward = get_total_reward(dir_path)

    file_path = dir_path + "/rewardsperlp-OCEAN.csv"
    df = pd.read_csv(file_path)

    # week = int(dir_path[31:33])
    today = datetime.now()
    week = today.strftime("%W")
    # df["week"] = week
    df = df.sort_values("OCEAN_amt", ascending=False).reset_index(drop=True)

    df["reward_perc_per_LP"] = df["OCEAN_amt"] / total_reward * 100
    df["week"] = week

    # lp_reward.loc[(lp_reward["reward_perc_per_LP"] >= 5)]
    df.sort_values(["OCEAN_amt"], ascending=[False]).reset_index(
        drop=True, inplace=True
    )
    df["LP_addr_label"] = df["LP_addr"].map(wallet_dict)
    return df


def load_nft_reward(dir_path):
    nft_reward = pd.DataFrame(
        columns=[
            "nft",
            "reward_amount",
            "reward_perc",
            "week",
        ]
    )
    # chainID,nft_addr,LP_addr,amt,token

    # total_reward = get_total_reward(dir_path)
    # for dir_path in glob(f"{data_dir}/*/", recursive=False):
    file_path = dir_path + "/rewardsinfo-OCEAN.csv"
    # week = int(dir_path[31:33])
    today = datetime.now()
    week = today.strftime("%W")
    df = pd.read_csv(file_path)

    x = []
    y = []
    for nft_addr in df["nft_addr"].unique():
        x.append(nft_addr)
        amt = df[df["nft_addr"] == nft_addr]["amt"].sum()
        y.append(amt)

    total_reward = sum(y)
    # total_reward[] = total_reward

    nft_reward = pd.DataFrame(
        {
            "nft": x,
            "reward_amount": y,
            "reward_perc": [y1 / total_reward * 100 for y1 in y],
            "week": week,
        }
    )
    # df["reward_perc_per_LP"] = df["OCEAN_amt"] / total_reward[r] * 100
    # nft_reward = nft_reward.append(nft_reward, ignore_index=True)
    # print(f'Total reward in week {r} is: {total_reward} Ocean' )
    # nft_reward = nft_reward.sort_values(["week"], ascending=[True]).reset_index(
    #     drop=True
    # )

    return nft_reward


def load_nft_lp_reward(dir_path, wallet_dict):
    nft_lp_reward = pd.DataFrame(
        columns=[
            "chainID",
            "nft_addr",
            "LP_addr",
            "amt",
            "token",
            "week",
            "LP_addr_label",
        ]
    )
    # for dir_path in glob(f"{data_dir}/*/", recursive=False):
    file_path = dir_path + "/rewardsinfo-OCEAN.csv"
    df = pd.read_csv(file_path)

    # week = int(dir_path[31:33])
    # df["week"] = week
    today = datetime.now()
    week = today.strftime("%W")
    # nft_lp_reward = nft_lp_reward.append(df, ignore_index=True)
    nft_lp_reward["LP_addr_label"] = nft_lp_reward["LP_addr"].map(wallet_dict)
    return nft_lp_reward


def label_race(row, chainID):
    nft_addr = row["nft_addr"]
    return query_nft_owner(nft_addr, chainID)


def load_nft_vol(dir_path, basetoken_addr, wallet_dict):
    nft_vol = pd.DataFrame(
        columns=["chainID", "basetoken_addr", "nft_addr", "vol_amt", "week"]
    )
    for chainID in (1, 56, 137, 1285):
        file_path = f"{dir_path}/nftvols-{chainID}.csv"
        today = datetime.now()
        week = today.strftime("%W")
        df = pd.read_csv(file_path)
        df["week"] = week
        print("querying nft owner")
        df["owner"] = df["nft_addr"].apply(lambda x: query_nft_owner(f'"{x}"', chainID))

        df.sort_values(["vol_amt"], ascending=[False]).reset_index(
            drop=True, inplace=True
        )
        nft_vol = nft_vol.append(df, ignore_index=True)

    nft_vol = nft_vol.loc[nft_vol["basetoken_addr"] == basetoken_addr]
    nft_vol = nft_vol.sort_values(["vol_amt"], ascending=[False]).reset_index(drop=True)
    nft_vol["owner_label"] = nft_vol["owner"].map(wallet_dict)

    nft_vol_total = nft_vol["vol_amt"].sum()

    nft_vol["vol_perc"] = nft_vol["vol_amt"] / nft_vol_total * 100
    return nft_vol


def get_total_reward(dir_path):
    file_path = dir_path + "/rewardsinfo-OCEAN.csv"
    df = pd.read_csv(file_path)
    y = 0
    for nft_addr in df["nft_addr"].unique():
        amt = df[df["nft_addr"] == nft_addr]["amt"].sum()
        y += amt

    # total_reward = sum(y)
    return y


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


def query_nft_owner(nft_addr, chainID):
    query = """
{
nfts(where: 
{
    address: %s
}) {
owner {
    id
}
}
}
""" % (
        nft_addr
    )
    # print(nft_addr)
    result = submitQuery(query, chainID)
    owner = result["data"]["nfts"][0]["owner"]["id"]
    return owner


#     query MyQuery {
#   nfts(where: {owner: "0x52b4943bae9cbda94f5f7e8b87a038bc96533a33"}) {
#     address
#     owner {
#       id
#     }
#   }
# }
# query MyQuery {
#   nfts(where: {address: "0xaedea2a290346b4b9dc9b4d0e8fa27f35bf4b89d"}) {
#     owner {
#       id
#     }
#     address
#   }
# }
