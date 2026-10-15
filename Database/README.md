# Finance challenge six industry instance

This is a frozen, real-data reference package for the question **When is retaining or changing a portfolio defensible?** It supports quantum risk estimation, analytical circuit design and optional QUBO/QAOA allocation modelling. It contains the organiser reference calculations, not just an empty student worksheet.

## Download source

Official data ZIP: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/10_Industry_Portfolios_CSV.zip

Construction: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/det_10_ind_port.html

Industry definitions: https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Siccodes10.zip

The official download has **ten** industries and several tables. This package extracts **six columns from Average Value Weighted Returns -- Monthly**, includes dividends, converts percentage returns to decimal returns, and freezes 120 observations from January 2015 to December 2024. Original ZIP files and SHA-256 fingerprints are retained. The original header identifies the 202608 CRSP database. French revises historical data; this is a fixed 2026-vintage historical exercise, not a reconstruction of the exact data release available in 2019.

These are U.S. listed-equity research portfolios. They are not European assets, individual stocks, ETF tickers or a liquidity/ESG dataset. Returns are not converted to euros. Credit: Eugene F. Fama and Kenneth R. French.

## The small instance

| Code | Industry | Between-industry starting weight |
|---|---|---:|
| NoDur | Consumer nondurables, including food, tobacco, textiles and apparel | 1/3 |
| Manuf | Manufacturing | 0 |
| Enrgy | Oil, gas and coal extraction and products | 0 |
| HiTec | Computers, software and electronic equipment | 0 |
| Hlth | Healthcare, medical equipment and drugs | 1/3 |
| Utils | Utilities | 1/3 |

Estimation uses January 2015–December 2019, **60 months**. The declared decision date is 31 December 2019. Later evaluation uses January 2020–December 2024, **60 separate months**, covering sharply different observed conditions. No later observation enters initial estimates or the initial scenario distribution. The sector selection is interpretable and manageable; it is not a statistically optimal or unbiased asset-universe selection.

The starting portfolio and a proposal to replace NoDur with HiTec are organiser choices. Both are declared before later evaluation. Three-of-six selection has 20 candidate allocations and six binary decision variables. The exact small state space is used for encoding checks, with no solver competition.

## Why the case has substance

In the frozen estimation sample, the proposed technology allocation has higher estimated monthly return than the starting allocation. However, a risk-sensitive investor's **hypothetical 20% technology cap** makes its one-third technology exposure inadmissible. A lower-return allocation can therefore be justified by a declared obligation.

Under the empirical scenario model, the proposed allocation's probability of exceeding a 3% one-month loss is 10% in the base case, 11.67% under the return stress and 15% under the covariance stress. The supplied risk-sensitive tolerance is 10%. These are conditional empirical model results, not future probabilities. A fixed-portfolio risk assessment and a requirement-based analytical investigation can therefore produce meaningful conclusions without finding a new optimum.

The current portfolio has no technology exposure, so shifting only technology returns does not change its outcomes. That is an interpretable exposure result, not a missing implementation. Unchanged conclusions are retained rather than forcing every stress to trigger a trade.

## Observations versus assumptions

`data/returns_6_industries_monthly.csv` contains only observed French returns. The six series are value weighted **within each industry**; the one-third allocation is a separate **between-industry** choice.

The base risk distribution assigns probability 1/60 to each observed joint estimation-month outcome. Equal weighting of past months is a modelling assumption, not an official forecast. The model is one-month and discrete; it is not an adequate standalone model of future tail risk.

Two stress tables are explicit hypothetical transformations:

- Shift HiTec returns down by 0.005, or 0.5 percentage points per month, leaving covariance unchanged.
- Move correlations 25% towards +1 while retaining each industry's sample mean and variance. A documented linear transformation of centred outcomes supplies a coherent joint distribution with that covariance.

Neither transformation is additional observed data. All thresholds, risk coefficients, concentration caps and penalties in `instance_config.json` are teaching parameters, not regulatory standards or values supplied by French. The technology cap is not a judgment that technology is inherently irresponsible. A liquidity condition needs additional evidence; this package does not invent liquidity values.

## Notebook and execution

1. Unzip the package.
2. Use Python 3.12 in a virtual environment.
3. Install `requirements.txt` with pip.
4. Open `Finance_Six_Industries_Verified.ipynb` in Jupyter or VS Code, then restart the kernel and run all cells.

No account, API key, hardware, GPU or paid compute is required. The notebook contains embedded data and helper definitions, so it can also run independently of the ZIP once dependencies are installed. If the companion CSV is present, its checksum is checked.

Two and five percentage point drift thresholds are evaluated for both declared allocations; all six cases are reported, including no-trade outcomes.

The notebook includes finite-shot **iterative amplitude estimation**, a verified reversible condition circuit, and two-layer QAOA with three fixed starts per mandate. Full notebook execution is the organiser reference workflow; student teams choose one contribution. QAOA runs are the most time-consuming portion. Use the recorded elapsed time as evidence for this environment, not as a guaranteed laptop runtime.

Quantum risk uses **seven logical qubits**: six scenario qubits for 60 observations, plus an event qubit. Four unused basis states have zero probability. Financial loss calculations and scenario marking are compiled outside the circuit; the quantum circuit estimates the marked probability. It does not calculate financial arithmetic directly from raw returns. Reported estimator intervals concern finite sampling conditional on the supplied distribution, not uncertainty about future markets.

The analytical circuit uses five qubits and three Toffoli gates. Its output indicates satisfaction of declared conditions, preserves inputs and clears a working qubit. The truth table is a technical building block; the higher-return versus exposure-cap conflict, evidence requirements and mandate sensitivity provide the analytical substance. Missing evidence withholds admission and is distinguished from a confirmed breach in the decision record.

QAOA selection uses the most probable feasible measured output, not a claim of global optimality. The penalty encoding is checked over all 64 bitstrings for each mandate/scenario setting.

## Files

- `Finance_Six_Industries_Verified.ipynb`: notebook with recorded outputs.
- `data/returns_6_industries_monthly.csv`: observed data; monthly decimal returns.
- `instance_config.json`: explicit instance and mandate assumptions.
- `source_manifest.json`: provenance, units, transformation and checksums.
- `finance_core.py`: reusable financial and quantum helpers.
- `requirements.txt`: tested direct dependency versions.
- `source/`: original official ZIP downloads.
- `results/`: estimates, scenario tables, decision maps, quantum outputs, sampled allocations, rule evaluation, diagrams and verification report.

## Verification scope

All notebook code cells are executed sequentially in a fresh IPython process, with outputs captured. This host prevents kernel sockets, so a Jupyter frontend/kernel connection is not verified here. Financial and quantum computations themselves are executed, not merely inspected. The machine-readable report records this distinction and actual checks. Ideal local simulation is used; hardware behavior, noise and investment validity are outside the verification.

Important checks include source-to-subset agreement; complete monthly chronology; percentage conversion; separate estimation/evaluation windows; portfolio mean/variance identities; covariance-stress validity; quantum state-preparation and event-probability identities; the complete condition truth table; QUBO/Ising energy equality for 576 basis-state cases; sampled allocation feasibility; and independent identities for buy-and-hold wealth and six declared rule evaluations.
