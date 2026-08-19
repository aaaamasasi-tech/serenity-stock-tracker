import json
import pandas as pd
import yfinance as yf

# Serenityの7層ボトルネック理論に基づくウォッチリスト
SERENITY_WATCHLIST = [
    {
        "symbol": "AXTI",
        "tier": "1. Raw Materials / InP Substrates",
        "thesis": "Indium Phosphide supply bottleneck",
    },
    {
        "symbol": "4063.T",  # 信越化学工業 (日本株は末尾に .T)
        "tier": "2. pBN Crucibles & Equipment",
        "thesis": "Single-supplier crucible constraint",
    },
    {
        "symbol": "SIVEF",  # Sivers Semiconductors (OTC)
        "tier": "4. CW Lasers (CPO Light Source)",
        "thesis": "CPO transition bottleneck (2027-2028)",
    },
    {
        "symbol": "AAOI",
        "tier": "5. Optical Modules Assembly",
        "thesis": "Hyperscaler capex direct beneficiary",
    },
    {
        "symbol": "AEHR",
        "tier": "6. Testing & Validation",
        "thesis": "Optical component validation bottleneck",
    },
]


def fetch_serenity_tracker_data():
    """Yahoo Financeからデータを取り込んで整形する"""
    tickers = [item["symbol"] for item in SERENITY_WATCHLIST]
    print(f"[{len(tickers)}銘柄のデータを取得中...]")

    # 一括で株価データを取得
    yf_tickers = yf.Tickers(" ".join(tickers))
    results = []

    for item in SERENITY_WATCHLIST:
        sym = item["symbol"]
        try:
            ticker_obj = yf_tickers.tickers[sym]
            info = ticker_obj.fast_info  # 安定して素早く取得

            current_price = info.last_price
            previous_close = info.previous_close

            # 前日比 (%) の計算
            if previous_close and current_price:
                change_pct = (
                    (current_price - previous_close) / previous_close
                ) * 100
                change_str = f"{change_pct:+.2f}%"
            else:
                change_str = "0.00%"

            # 時価総額の計算 ($M / $B 表記)
            market_cap = info.market_cap
            if market_cap:
                if market_cap >= 1e9:
                    mcap_str = f"${market_cap / 1e9:.2f}B"
                else:
                    mcap_str = f"${market_cap / 1e6:.1f}M"
            else:
                mcap_str = "N/A"

            results.append(
                {
                    "symbol": sym,
                    "tier": item["tier"],
                    "thesis": item["thesis"],
                    "price": round(current_price, 2)
                    if current_price
                    else "N/A",
                    "prev_close": round(previous_close, 2)
                    if previous_close
                    else "N/A",
                    "change_pct": change_str,
                    "market_cap": mcap_str,
                }
            )

        except Exception as e:
            print(f"エラー発生 ({sym}): {e}")
            # エラー時も全体の処理を止めずにスキップ
            results.append(
                {
                    "symbol": sym,
                    "tier": item["tier"],
                    "thesis": item["thesis"],
                    "price": "N/A",
                    "prev_close": "N/A",
                    "change_pct": "N/A",
                    "market_cap": "N/A",
                }
            )

    return results


if __name__ == "__main__":
    # 株価取得
    data = fetch_serenity_tracker_data()

    # 1. 自動更新用の JSON ファイルとして保存
    with open("serenity_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    # 2. ログ確認用（GitHub Actionsの実行ログで見やすいよう出力）
    df = pd.DataFrame(data)
    print("\n=== 最新取得データ ===")
    print(
        df[["symbol", "tier", "price", "change_pct", "market_cap"]].to_string(
            index=False
        )
    )
    print("\n`serenity_data.json` の作成が完了しました。")
