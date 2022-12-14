import sys
from datetime import datetime

today = datetime.now()

from enforce_typing import enforce_types

from utils.load_data import (
    # get_total_reward,
    load_ve_balance,
    load_ve_allocation_pct,
    load_lp_reward,
    load_nft_lp_reward,
    load_nft_vol,
    load_nft_reward,
    cal_ve_allocation,
)


wallet_dict = {
    "0x8475b523b5fa2db7b77eb5f14edabdefc2102698": "psdn",
    "0x2e434c18ae93ee2da937222ea5444692ed265ac0": "whale1",
    "0xc1b8665bae4389d95d558ff3a0e58c2a24625f63": "whale2",
    "0xac517ed8283d629dd01fac97ece9f91b218203f9": "whale3",
    "0xf0a8802509421df907188434d4fc230cf9271672": "shrimp1",
    "0xcf8a4b99640defaf99acae9d770dec9dff37927d": "shrimp2",
    "0x663052ad99b85a8c35040c4fd1cc87620f4b61f1": "shrimp3",
    "0xeb18bad7365a40e36a41fb8734eb0b855d13b74f": "shrimp1",
}


def top_table_markdown(df, top=5):
    top_table_markdown = df.head(top).to_markdown(index=False)
    return top_table_markdown


def top_nft_allocation(nft_vol, ve_allocation):
    for nft_addr in list(nft_vol["nft_addr"].head(5).unique()):
        _df = ve_allocation.loc[ve_allocation["nft_addr"] == nft_addr]
        _df = _df.sort_values(["allocation"], ascending=[False]).reset_index(drop=True)
        top_nft_allocation = top_table_markdown(
            _df[["LP_addr", "allocation", "LP_addr_label", "percent", "balance"]]
        )
    return top_nft_allocation


@enforce_types
def do_nft_vol(dir_path, markdown_file, text):
    # total_reward = get_total_reward(dir_path)

    lp_reward = load_lp_reward(dir_path, wallet_dict)
    ve_balance = load_ve_balance(dir_path)
    ve_allocation_pct = load_ve_allocation_pct(dir_path)
    ve_allocation = cal_ve_allocation(ve_balance, ve_allocation_pct, wallet_dict)
    basetoken_addresses = [
        "0xpolygon",
        "0x282d8efce846a88b159800bd4130ad77443fa1a1",
        "0x967da4048cd07ab37855c090aaf366e4ce1b9f48",
    ]
    nft_vol = {}
    # top_nft_allocation = {}
    for basetoken_addr in basetoken_addresses:
        nft_vol[basetoken_addr] = load_nft_vol(dir_path, basetoken_addr)

    # for basetoken_addr in basetoken_addresses:
    #     top_nft_allocation[basetoken_addr] = top_nft_allocation(
    #         nft_vol[basetoken_addr], ve_allocation
    #     )

    # nft_lp_reward = load_nft_lp_reward(dir_path, wallet_dict)
    # nft_reward = load_nft_reward(dir_path)

    top_reward_receiver = top_table_markdown(lp_reward, top=10)

    dt = today.strftime("%W-%a-%Y-%m-%d")

    markdown_text = f"""# Week-{dt} 
## Top NFT volume
### Polygon, base token Ocean
{top_table_markdown(nft_vol['0x282d8efce846a88b159800bd4130ad77443fa1a1'][['nft_addr', 'vol_amt','vol_perc']])}

### Ethereum, base token Ocean
{top_table_markdown(nft_vol['0x967da4048cd07ab37855c090aaf366e4ce1b9f48'][['nft_addr', 'vol_amt','vol_perc']])}
"""
    with open(markdown_file, "w") as f:
        f.write(markdown_text)


@enforce_types
def do_allocation(dir_path, markdown_file, text):
    ve_balance = load_ve_balance(dir_path)
    ve_allocation_pct = load_ve_allocation_pct(dir_path)
    ve_allocation = cal_ve_allocation(ve_balance, ve_allocation_pct, wallet_dict)

    # dt = today.strftime("%W-%a-%Y-%m-%d")
    _ve_allocation = ve_allocation[
        ["nft_addr", "LP_addr", "allocation", "LP_addr_label"]
    ]
    markdown_text = f"""## Top LP
{top_table_markdown(_ve_allocation,10)}

"""
    with open(markdown_file, "a") as f:
        f.write(markdown_text)


@enforce_types
def do_main():
    assert sys.argv[1] == "eda"
    dir_path = sys.argv[2]
    dt = today.strftime("%W-%a-%Y-%m-%d")
    if sys.argv[3] == "report":
        markdown_file = f"strat/Reports/report-{dt}.MD"
        text = "NFT volume"
        do_nft_vol(dir_path, markdown_file, text)
        text = "Allocation"
        do_allocation(dir_path, markdown_file, text)


if __name__ == "__main__":
    do_main()
