# Cryptocurrency-Dashboard

  A web application to view the percentage difference and do financial technical analysis on real-time cryptocurrency data using flask web framework, ccxt trading api and tulipy library. 
  This web app basically asks the user to sign-in if he is already a custoemr else he can sign-up, after succesful login the application asks the customer to select the coin pair on which we wants to do the analysis. If the coin exist, then using ccxt api the real-time cryptocurrency data is fetched and stored in a feather file. After this the customer can select either percentage analysis or financial data analysis on the fetched data and finally the respective result is displayed. Financial data analysis is done by using tulipy library.


## CCXT

  The ***CCXT library*** is used to connect and trade with cryptocurrency exchanges and payment processing services worldwide. It provides quick access to market data for storage, analysis, visualization, indicator development, algorithmic trading, strategy backtesting, bot programming, and related software engineering.

  It is intended to be used by coders, developers, technically-skilled traders, data-scientists and financial analysts for building trading algorithms.

  Current feature list:

  support for many cryptocurrency exchanges — more coming soon
  fully implemented public and private APIs
  optional normalized data for cross-exchange analytics and arbitrage
  an out of the box unified API that is extremely easy to integrate
  works in Node 7.6+, Python 2 and 3, PHP 5.4+, and web browsers

## TULIPY

  Tulip Indicators (TI) is a library of functions for technical analysis of financial time series data. It is written in ANSI C for speed and portability.

  Tulip Indicators is intended for programmers. If you're not a programmer, you may be more interested in Tulip Cell, the Excel add-in, or Tulip Charts, the full featured stock charting program. Both rely on Tulip Indicators for their indicator math. Tulip Indicators currently implements 104 indicators. Bindings are available for many other programming languages too. One such binding for python is ***tulipy***.


## FEATHER

  ***Feather*** is a fast, lightweight, and easy-to-use binary file format for storing data frames. It has a few specific design goals:

  * Lightweight, minimal API: make pushing data frames in and out of memory as simple as possible

  * Language agnostic: Feather files are the same whether written by Python or R code. Other languages can read and write Feather files, too.

  * High read and write performance. When possible, Feather operations should be bound by local disk performance.
  <br>  <br>

**Environment Setup**

python -m pip install -r requirements.txt

![Screenshot](screenshots/home.png)
