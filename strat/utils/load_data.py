import pandas as pd
from enforce_typing import enforce_types
import requests
from datetime import datetime

wallet_dict = {
    "0x8475b523b5fa2db7b77eb5f14edabdefc2102698": "psdn",
    "0x2e434c18ae93ee2da937222ea5444692ed265ac0": "whale1",
    "0xc1b8665bae4389d95d558ff3a0e58c2a24625f63": "whale2",
    "0xac517ed8283d629dd01fac97ece9f91b218203f9": "whale3",
    "0xf0a8802509421df907188434d4fc230cf9271672": "wallet_1",
    "0xcf8a4b99640defaf99acae9d770dec9dff37927d": "wallet_2",
    "0x663052ad99b85a8c35040c4fd1cc87620f4b61f1": "wallet_3",
    "0xeb18bad7365a40e36a41fb8734eb0b855d13b74f": "wallet_4",
    "0x8978be1b2082d10ea95533d2897ddab53afb97e9": "wallet_5",
    "0x655efe6eb2021b8cefe22794d90293aec37bb325": "wallet_6",
    "0xce74a5886ea7a8a675d8fb5fc11a697a23fe1dc8": "wallet_7",
    "0xf062d1b3f658ad32f7896a76807b05ba7a9e7720": "wallet_8",
}

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
today = datetime.now()
week = today.strftime("%W")


def load_ve_balance(dir_path):
    file_path = dir_path + "/vebals.csv"
    df = pd.read_csv(file_path)
    df["week"] = week

    total_ve = df["balance"].sum()
    df["perc"] = df["balance"] / total_ve * 100

    df = df.sort_values(["balance"], ascending=[True]).reset_index(drop=True)
    return df


def load_ve_allocation_pct(dir_path):
    file_path = dir_path + "/allocations.csv"
    df = pd.read_csv(file_path)

    df["week"] = week

    return df


def cal_ve_allocation(ve_balance, ve_allocation_pct, wallet_dict):
    ve_allocation = pd.merge(
        ve_balance, ve_allocation_pct, on=["LP_addr", "week"], how="left"
    ).reset_index(drop=True)
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

    total_reward = get_total_reward(dir_path)

    file_path = dir_path + "/rewardsperlp-OCEAN.csv"
    df = pd.read_csv(file_path)

    df = df.sort_values("OCEAN_amt", ascending=False).reset_index(drop=True)

    df["reward_perc_per_LP"] = df["OCEAN_amt"] / total_reward * 100
    df["week"] = week

    df.sort_values(["OCEAN_amt"], ascending=[False]).reset_index(
        drop=True, inplace=True
    )
    df["LP_addr_label"] = df["LP_addr"].map(wallet_dict)
    return df


def load_nft_reward(dir_path):

    file_path = dir_path + "/rewardsinfo-OCEAN.csv"

    df = pd.read_csv(file_path)
    df["week"] = week
    return df


def load_nft_lp_reward(dir_path, wallet_dict):
    file_path = dir_path + "/rewardsinfo-OCEAN.csv"
    df = pd.read_csv(file_path)
    df["week"] = week

    df["LP_addr_label"] = df["LP_addr"].map(wallet_dict)
    df = df.sort_values(["amt"], ascending=[False]).reset_index(drop=True)
    return df


def load_nft_vol(dir_path, basetoken_addr, wallet_dict):
    nft_vol = pd.DataFrame(
        columns=["chainID", "basetoken_addr", "nft_addr", "vol_amt", "week"]
    )
    for chainID in (1, 56, 137, 1285):
        file_path = f"{dir_path}/nftvols-{chainID}.csv"

        df = pd.read_csv(file_path)
        df["week"] = week
        df["owner"] = df["nft_addr"].apply(lambda x: query_nft_owner(f'"{x}"', chainID))

        df.sort_values(["vol_amt"], ascending=[False]).reset_index(
            drop=True, inplace=True
        )
        nft_vol = pd.concat([nft_vol, df], ignore_index=True, sort=False)

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

    return y


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
