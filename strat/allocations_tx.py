import requests

from datetime import datetime
import os

# os.chdir(".")
print(os.getcwd())
# from util.graphutil import submitQuery
from enforce_typing import enforce_types
import json

_RAW_CHAIN_DATA = [
    (8996, "development", "OCEAN"),
    (1, "mainnet", "ETH"),
    (3, "ropsten", "ETH"),
    (4, "rinkeby", "ETH"),
    (5, "goerli", "ETH"),
    (56, "bsc", "BNB"),
    (137, "polygon", "MATIC"),
    (246, "energyweb", "EWT"),
    (1287, "moonbase", "MOVR"),
    (1285, "moonriver", "MOVR"),
    (80001, "mumbai", "MATIC"),
]
_CHAINID_TO_NETWORK = {x[0]: x[1] for x in _RAW_CHAIN_DATA}
_NETWORK_TO_CHAINID = {
    network: chainID for chainID, network in _CHAINID_TO_NETWORK.items()
}
DEV_CHAINID = _NETWORK_TO_CHAINID["development"]


@enforce_types
def chainIdToNetwork(chainID: int) -> str:
    """Returns the network name for a given chainID"""
    return _CHAINID_TO_NETWORK[chainID]


@enforce_types
def chainIdToSubgraphUri(chainID: int) -> str:
    """Returns the subgraph URI for a given chainID"""
    sg = "/subgraphs/name/oceanprotocol/ocean-subgraph"
    if chainID == DEV_CHAINID:
        return "http://127.0.0.1:9000" + sg

    network_str = chainIdToNetwork(chainID)
    return f"https://v4.subgraph.{network_str}.oceanprotocol.com" + sg


def submitQuery(query: str, chainID: int) -> dict:
    subgraph_url = chainIdToSubgraphUri(chainID)
    request = requests.post(subgraph_url, "", json={"query": query})
    if request.status_code != 200:
        raise Exception(f"Query failed. Return code is {request.status_code}\n{query}")

    result = request.json()

    return result


def get_ethereum_block_from_ts(ts: int):
    etherscan_api_token = "FM61KFUCQW6457RMVWQASMR8UKM2ZITJU9"
    r = requests.get(
        f"https://api.etherscan.io/api?module=block&action=getblocknobytime&timestamp={ts}&closest=before&apikey={etherscan_api_token}",
    )
    return int(r.json()["result"])


def query_allocation_txs(timestamp: int):
    query = (
        """
    {
        veAllocationUpdates(where: {
            timestamp_gte: %s,
            veAllocation_: {allocated_gt: "0"}
            }) {
                timestamp
                veAllocation {
                    allocated
                    nftAddress
                    allocationUser {
                        id
                    }
                    chainId
        }
        }
    }   
        """
        % timestamp
    )
    result = submitQuery(query, 1)
    if "errors" in result:
        raise AssertionError(result)
    new_allocations = result["data"]["veAllocationUpdates"]
    return new_allocations
    # with open("strat/tmp/data.json", "w") as f:
    #     json.dump(new_allocations, f)


def query_datatoken_of_nft(nft, chainId):
    query = (
        """
    {tokens(
    where: {
        nft: %s, 
        isDatatoken: true}
  ) {
    id
    name
    symbol
  }
}
        """
        % nft
    )
    result = submitQuery(query, chainId)
    if "errors" in result:
        raise AssertionError(result)
    datatoken = result["data"]["tokens"]
    return datatoken


@enforce_types
def do_main():
    ts_current = int(datetime.utcnow().timestamp())
    ts_6hrs_ago = ts_current - 6 * 3600
    block = get_ethereum_block_from_ts(ts_6hrs_ago)
    query_allocation_txs(block)


if __name__ == "__main__":
    do_main()
