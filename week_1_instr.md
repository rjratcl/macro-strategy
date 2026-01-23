
## **Week 1: Data Pipeline - Canadian Core + Global Context**

**Goal:** By end of week, you can fetch data from multiple sources, store it in SQLite, and retrieve it for analysis.

---

### **Task 1: Project Setup (30 minutes)**

**What you're doing:**
- Create directory structure
- Initialize git repo
- Set up virtual environment
- Create requirements.txt

**Decisions to make:**
- Which packages do you actually need? (Start minimal)
- What folder structure makes sense? (data/, src/, tests/, logs/, notebooks/)
- .gitignore: what shouldn't be committed? (database files, logs, venv)

**How you'll know it worked:**
- Can activate venv
- Can install packages from requirements.txt
- Git is tracking your files (but not the venv or data)

---

### **Task 2: Database Design (1-2 hours)**

**What you're doing:**
- Design your schema (what tables, what columns)
- Write code to create the database and tables
- Add indexes for query performance

**Key decisions:**
- **Table structure:** Do you want one big table with all time series, or separate tables per data type?
- **Primary key:** How do you uniquely identify a row? (series_id + date?)
- **Metadata:** Do you store info *about* the series separately?
- **Data types:** TEXT vs VARCHAR? REAL vs FLOAT? Does it matter in SQLite?

**Questions to answer:**
- How will you handle the fact that BoC has daily data but StatCan is monthly?
- Should you store data in CAD or USD, or both?
- What if you fetch the same data twice - insert duplicate or update?

**How you'll know it worked:**
- Database file exists
- You can open it (sqlitebrowser or sqlite3 CLI) and see empty tables
- Running your creation script twice doesn't error (CREATE IF NOT EXISTS)

---

### **Task 3: Bank of Canada API Integration (2-3 hours)**

**What you're doing:**
- Read BoC Valet API documentation
- Write code to fetch a single series (start with policy rate)
- Parse the JSON response into a pandas DataFrame
- Handle errors (API down, bad series ID, network issues)

**BoC API basics:**
- Base URL: `https://www.bankofcanada.ca/valet/observations/`
- Format: `/[series_id]/json`
- Returns JSON with observations array

**Series to fetch (start with these):**
- `V122530` - BoC policy rate
- `FXCADUSD` - CAD/USD exchange rate
- `V122521` - 5-year GoC bond yield
- `V122531` - 10-year GoC bond yield

**Decisions:**
- How do you handle date parsing? (BoC uses YYYY-MM-DD format)
- What if API returns partial data?
- Do you fetch all history every time or only new data?
- How do you log what you fetched?

**How you'll know it worked:**
- You can print a DataFrame with dates and values
- Running it twice gives you the same data
- You can see in logs when it ran and what it fetched

---

### **Task 4: Insert Data Into Database (1-2 hours)**

**What you're doing:**
- Take the DataFrame from Task 3
- Insert it into your database
- Handle duplicate dates (update vs error vs ignore)

**Design decisions:**
- Do you insert one row at a time or bulk insert?
- What happens if you try to insert the same date twice?
- Do you update metadata (last_updated timestamp)?
- How do you verify it actually worked?

**Edge cases to handle:**
- Empty DataFrame (API returned nothing)
- NaN values in the data
- Date already exists in database

**How you'll know it worked:**
- Open database in sqlitebrowser - see rows in your table
- Run query: `SELECT COUNT(*) FROM time_series WHERE series_id = 'V122530'`
- Fetch same data twice - should update, not duplicate

---

### **Task 5: Retrieve Data From Database (1 hour)**

**What you're doing:**
- Write function to get a series back as DataFrame
- Support date filtering (start_date, end_date)
- Handle missing series gracefully

**What this needs to do:**
- Given a series_id, return DataFrame with dates as index
- Optionally filter to date range
- Return empty DataFrame if series doesn't exist (don't crash)

**How you'll know it worked:**
- Fetch 'V122530' - get back a DataFrame
- Filter to 2024 only - get back smaller DataFrame
- Fetch fake series 'DOESNT_EXIST' - get empty DataFrame, not an error

---

### **Task 6: FRED API Integration (2-3 hours)**

**What you're doing:**
- Same as Task 3, but for FRED (US data)
- FRED requires API key (free, register at fred.stlouisfed.org)
- Different JSON structure than BoC

**FRED series to fetch:**
- `DFF` - Fed Funds Rate
- `DGS10` - 10-Year Treasury
- `VIXCLS` - VIX
- `DCOILWTICO` - WTI Crude Oil

**Key differences from BoC:**
- FRED requires API key in URL
- Different JSON structure (observations array has different field names)
- Some series have weird values (".") for missing data

**Decisions:**
- Do you hard-code API key or use environment variable?
- How do you handle missing values marked as "."?
- Can you reuse code from Task 3 or do you need separate function?

**How you'll know it worked:**
- All 4 series in your database
- Can retrieve DFF and plot Fed Funds rate history
- Code handles missing values without crashing

---

### **Task 7: Build Reusable Functions (1-2 hours)**

**What you're doing:**
- Refactor Tasks 3-6 into clean, reusable functions
- Create a main script that fetches all your core series
- Add proper error handling and logging

**Goal structure:**
```
src/
├── database.py        # Database operations (create, insert, retrieve)
├── fetch_boc.py       # BoC API functions
├── fetch_fred.py      # FRED API functions
├── update_data.py     # Main script that runs everything
└── config.py          # Store series IDs, API keys
```

**What update_data.py should do:**
1. Connect to database (create if doesn't exist)
2. Loop through list of series
3. Fetch from appropriate API
4. Insert into database
5. Log success/failure for each series

**How you'll know it worked:**
- Run `python src/update_data.py` - fetches all data
- Check database - all series present
- Run again - updates data, doesn't duplicate
- Check logs - clear record of what happened

---

### **Task 8: Data Validation (1-2 hours)**

**What you're doing:**
- Write checks to verify data quality
- Create simple report showing what you have

**Checks to implement:**
- Are there gaps in daily/monthly series?
- Are values in reasonable ranges? (rates 0-10%, FX 0.6-0.9)
- When was each series last updated?
- How many observations per series?

**Output:**
- Print summary: "V122530: 2,847 observations, 2015-01-02 to 2025-01-22, last updated 2025-01-22"
- Flag any issues: "Warning: CAD_USD has gap between 2020-03-15 and 2020-03-18"

**How you'll know it worked:**
- Run validation script - get summary of all series
- Intentionally corrupt data - validation catches it
- Can quickly see if data fetch failed

---

### **Task 9: Testing (1-2 hours)**

**What you're doing:**
- Write pytest tests for your core functions
- Test database operations
- Test API fetching (at least check parsing logic)

**Tests to write:**
- `test_database_creates_tables()` - verify schema
- `test_insert_and_retrieve()` - roundtrip test
- `test_duplicate_dates_update()` - verify upsert behavior
- `test_boc_parse_response()` - parse mock BoC JSON
- `test_fred_parse_response()` - parse mock FRED JSON
- `test_data_validation()` - verify checks work

**How you'll know it worked:**
- Run `pytest -v` - all tests pass
- Break something intentionally - test fails
- Tests run in seconds (use in-memory test database)

---

### **Task 10: Documentation & Cleanup (30 minutes)**

**What you're doing:**
- Write README.md explaining what you built
- Document which series you're tracking and why
- Add comments to confusing code sections
- Commit everything to git

**README should include:**
- What this project does
- How to set it up (venv, requirements, API keys)
- How to run it (`python src/update_data.py`)
- What data you're collecting
- File structure explanation

**How you'll know it worked:**
- Someone else (future you in 3 months) could clone repo and run it
- Git history shows logical commits, not one giant commit
- Code is commented enough to remember what you were thinking

---

## **Week 1 Success Criteria**

By Friday evening, you should be able to:

1. **Run one command** (`python src/update_data.py`) that fetches all your data
2. **Check database** and see Canadian + US data from 2015-present
3. **Run tests** (`pytest`) and they all pass
4. **Retrieve any series** in a Jupyter notebook for exploratory analysis
5. **Verify data quality** with validation script

**Proof it worked:**
```python
# In Jupyter notebook
from src.database import get_series

boc_rate = get_series('V122530', start_date='2020-01-01')
fed_rate = get_series('DFF', start_date='2020-01-01')

import matplotlib.pyplot as plt
plt.plot(boc_rate.index, boc_rate['value'], label='BoC')
plt.plot(fed_rate.index, fed_rate['value'], label='Fed')
plt.legend()
plt.title('BoC vs Fed Policy Rates')
plt.show()
```

If you can make that plot, Week 1 is done.

---

## **Common Sticking Points (Where to Ask for Help)**

- **BoC API returns weird JSON** - parsing the nested structure
- **FRED API authentication** - getting API key into code safely
- **Date handling** - timezone issues, string vs datetime
- **SQL syntax** - INSERT vs INSERT OR REPLACE, PRIMARY KEY syntax
- **Pandas date indexing** - setting index, filtering by date
- **Testing** - mocking API calls, fixture setup

When you hit these, ask. But try first - the struggle is where learning happens.

---
