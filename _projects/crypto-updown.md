---
title: Pricing Short-Dated Crypto Binaries on Polymarket
slug: crypto-updown
summary: A pricing model, market-data recorder and order-book simulator for 15-minute and hourly crypto up/down contracts. None of the strategies beat the market after realistic execution.
status: Complete
year: 2026
order: 2
tags: [prediction markets, digital options, market microstructure, volatility]
stack: [Python, Parquet, SQLite, Deribit API]
image: /assets/img/covers/crypto-updown.png
hero: false
repo: https://github.com/suhjy1/trading_crypto_showcase
---

## Introduction

Polymarket lists 15-minute and hourly "Up or Down" contracts on BTC, ETH, SOL and XRP. Each contract pays $1 if the price at the end of the window is at or above the price at the start. The underlying assets trade on exchanges that are much faster than the prediction market. My question was whether a market maker or taker pricing off those faster feeds could earn money after fees and adverse selection. To answer it, I built a pricing model, a market-data recorder and an order-book simulator.

## The contract

The two tenors settle differently, and this mattered a lot for pricing. The hourly contract settles on a Binance 1-minute candle, open against close, which makes it a standard European digital. The 15-minute contract settles on Chainlink's 60-second TWAP at both the start and the end of the window, which makes it an arithmetic Asian digital with an uncertain strike.

Since the windows are only minutes long, drift and discounting are negligible. Pricing comes down to forecasting the variance to settlement and modeling the distribution of standardized moves. Near expiry, the known part of the TWAP matters most. With spot 1 bp above the strike and 30 to 45 seconds left, a point-price model is about 19c away from the TWAP price (Exhibit 1).

![Exhibit 1](/assets/img/covers/crypto-updown.png)

Exhibit 1: P(up) for a 15-minute contract with spot held 1 bp above the strike, priced as a TWAP digital (blue) and as a point digital (gold), at 60, 45, 30 and 15 seconds before expiry.
{: .text-muted }

## Results

The short answer is no. None of the strategies beat the market after realistic execution. The traded price beat every standalone model, and better tail modeling was worth far less than the market's information advantage. A maker replay carried +6c of model edge at the decision and gave back −7c by settlement, meaning the model's price was wrong by more than the half-spread on exactly the fills it got. Two pre-registered maker strategies, run through a simulator calibrated against on-chain fills, both failed.

The more useful results are how I established this and where the edge goes. The repository README covers the settlement-source reconstruction, the variance and distribution tests, the Deribit volatility surface, and the per-fill P&L decomposition.

## Evaluation standards

All comparisons are paired on identical rows, with day- or market-clustered standard errors. Strategy results get a wild cluster bootstrap verdict, and a result only counts as positive if its lower bound stays above zero after dropping any single day and the two best days. Hypotheses and pass rules were pre-registered, and the held-out period was never read.
