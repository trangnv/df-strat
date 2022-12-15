import sys
from datetime import datetime
from enforce_typing import enforce_types

from utils.load_data import (
    load_ve_balance,
    load_ve_allocation_pct,
    load_lp_reward,
    load_nft_vol,
    load_nft_lp_reward,
    cal_ve_allocation,
    wallet_dict,
)

today = datetime.now()


def top_table_markdown(df, top=5):
    top_table_markdown = df.head(top).to_markdown(index=False)
    return top_table_markdown


# def top_nft_allocation(nft_vol, ve_allocation): # get top LP for each nft_addr
#     for nft_addr in list(nft_vol["nft_addr"].head(5).unique()):
#         _df = ve_allocation.loc[ve_allocation["nft_addr"] == nft_addr]
#         _df = _df.sort_values(["allocation"], ascending=[False]).reset_index(drop=True)
#         top_nft_allocation = top_table_markdown(
#             _df[["LP_addr", "allocation", "LP_addr_label", "percent", "balance"]]
#         )
#     return top_nft_allocation


@enforce_types
def do_nft_vol(dir_path, markdown_file, hour=""):
    basetoken_addresses = [
        "0xpolygon",
        "0x282d8efce846a88b159800bd4130ad77443fa1a1",
        "0x967da4048cd07ab37855c090aaf366e4ce1b9f48",
    ]
    nft_vol = {}
    for basetoken_addr in basetoken_addresses:
        nft_vol[basetoken_addr] = load_nft_vol(dir_path, basetoken_addr, wallet_dict)

    markdown_text = f"""# ---{hour}---
## Top NFT volume
### Polygon, base token Ocean
{top_table_markdown(nft_vol['0x282d8efce846a88b159800bd4130ad77443fa1a1'][['nft_addr', 'owner_label','vol_amt','vol_perc']])}

### Ethereum, base token Ocean
{top_table_markdown(nft_vol['0x967da4048cd07ab37855c090aaf366e4ce1b9f48'][['nft_addr', 'owner_label','vol_amt','vol_perc']])}

"""
    with open(markdown_file, "a") as f:
        f.write(markdown_text)


@enforce_types
def do_allocation(dir_path, markdown_file):
    ve_balance = load_ve_balance(dir_path)
    ve_allocation_pct = load_ve_allocation_pct(dir_path)
    ve_allocation = cal_ve_allocation(ve_balance, ve_allocation_pct, wallet_dict)

    psdn_allocation = ve_allocation[
        ["chainID", "balance", "perc", "nft_addr", "allocation", "percent"]
    ].loc[ve_allocation["LP_addr_label"] == "psdn"]
    _ve_allocation = ve_allocation[
        ["chainID", "nft_addr", "LP_addr", "allocation", "percent", "LP_addr_label"]
    ]
    markdown_text = f"""## Top LP
{top_table_markdown(_ve_allocation,10)}

## PSDN allocation
{top_table_markdown(psdn_allocation)}

"""
    with open(markdown_file, "a") as f:
        f.write(markdown_text)


@enforce_types
def do_nft_lp_reward(dir_path, markdown_file):
    nft_lp_reward = load_nft_lp_reward(dir_path, wallet_dict)
    _df = nft_lp_reward[["nft_addr", "LP_addr", "amt", "LP_addr_label"]]
    markdown_text = f"""## Reward
{top_table_markdown(_df, 10)}
"""
    with open(markdown_file, "a") as f:
        f.write(markdown_text)


@enforce_types
def do_main():
    assert sys.argv[1] == "eda"
    dir_path = sys.argv[2]

    if sys.argv[3] == "weekly-report":
        dt = today.strftime("%W-%Y-%m-%d-%a")
        markdown_file = f"strat/reports/{dt}-weekly.MD"

        # nft volume report
        do_nft_vol(dir_path, markdown_file)

        # allocation report
        do_allocation(dir_path, markdown_file)

        # reward report
        do_nft_lp_reward(dir_path, markdown_file)

    if sys.argv[3] == "daily-report":
        dt = today.strftime("%W-%Y-%m-%d-%a")
        markdown_file = f"strat/reports/{dt}-daily.MD"

        # nft volume report
        hour = today.strftime("%H:%M")
        do_nft_vol(dir_path, markdown_file, hour=f"Time {hour}")

        # allocation report
        do_allocation(dir_path, markdown_file)

        # reward report
        do_nft_lp_reward(dir_path, markdown_file)


if __name__ == "__main__":
    do_main()
