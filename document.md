Here is the complete reorganized document with code snippets and descriptions.

---

# Smart Inventory Monitoring & Forecasting Application
## Complete User & Technical Documentation

---

## Part 1: How to Use the App (Absolute Beginner Guide)

### Starting the App

1. Open terminal (command prompt)
2. Navigate to project folder:
   ```bash
   cd C:\Users\HP\Desktop\smart-invento-app
   ```
3. Activate virtual environment:
   ```bash
   venv\Scripts\activate
   ```
4. Run the app:
   ```bash
   streamlit run app.py
   ```
5. Your browser opens automatically to `http://localhost:8501`

---

### Menu Options (Left Sidebar)

#### 1. Dashboard
**What you see:** A table of all items and a bar chart

| Column | Meaning |
|--------|---------|
| name | Item name (e.g., "Milk", "Tomato") |
| current_quantity | How many units you have right now |
| reorder_point | When stock hits this number, time to reorder |
| lead_time_days | Days between ordering and receiving |

**What to do:** Just look. No actions here.

---

#### 2. Manage Items

**Add New Item:**
- Type item name (e.g., "Coffee Beans")
- Enter starting quantity (e.g., 100)
- Set reorder point (e.g., 20)
- Set lead time in days (e.g., 5)
- Click "Add Item"

**Delete Item:**
- Select item from dropdown
- Click "Delete"

---

#### 3. Record Transaction

**Purpose:** Log daily sales or new stock arrivals

**Steps:**
1. Select item from dropdown
2. Choose "Sale" (customer bought) or "Purchase" (you bought more)
3. Enter quantity
4. Click "Record"

**What happens automatically:**
- Sale → Stock goes down
- Purchase → Stock goes up
- Date is recorded automatically (today's date)

---

#### 4. Forecast & Trends

**Purpose:** Predict when you will run out of stock

**How to use:**
1. Select an item from dropdown
2. View two numbers:

| Number | Meaning | Example |
|--------|---------|---------|
| Predicted Daily Demand | Average units sold per day | 15 units/day |
| Days Until Stockout | When you will run out | 5.5 days |

**The Chart:** Shows daily sales for the last 30 days (each bar = one day)

**What to do:** Check this page daily to plan reorders.

---

#### 5. Alerts

**Purpose:** Automatic warnings

**Two types of alerts:**

| Alert | Meaning | Example |
|-------|---------|---------|
| LOW STOCK | Current stock ≤ Reorder point | "Milk has 8 left (Reorder: 10)" |
| PREDICTED STOCKOUT | Will run out before new stock arrives | "Milk runs out in 3 days, delivery takes 5 days" |

**What to do:** Check this page every morning. Reorder any items shown.

---

### Terms Explained Simply

| Term | Simple Meaning |
|------|----------------|
| Stock | How many you have |
| Reorder point | Minimum before you must reorder |
| Lead time | Days from order to delivery |
| Demand | How many customers buy per day |
| Stockout | Running out of something |
| Forecasting | Guessing future sales using past sales |
| Exponential Smoothing | A math formula that trusts recent sales more |

---

### Typical Daily Workflow

1. **Morning (9:00 AM):** Open Alerts page → Reorder anything shown
2. **During day:** Record each sale as it happens
3. **End of day (5:00 PM):** Check Forecast page → See upcoming stockouts
4. **Monday morning:** Check Dashboard → Review all stock levels

---

## Part 2: Core Functions Explained with Code

This section shows the most important functions in the application, what they do, and how they work.

---

### Function 1: `add_item()` - Adding New Products

**File:** `inventory.py`

**What it does:** Creates a new item in the database with initial stock, reorder point, and lead time.

**Code:**
```python
def add_item(name, initial_qty=0, reorder_point=10, lead_time=7):
    session = get_session()
    item = Item(name=name, current_quantity=initial_qty, 
                reorder_point=reorder_point, lead_time_days=lead_time)
    session.add(item)
    session.commit()
    item_id = item.id
    session.close()
    return item_id
```

**Explanation:**
- `session = get_session()` → Opens connection to database
- `Item(name=..., current_quantity=...)` → Creates new item object
- `session.add(item)` → Prepares to save
- `session.commit()` → Actually saves to database
- `return item_id` → Gives back the ID number for reference

**Example:** `add_item("Milk", 50, 10, 3)` adds Milk with 50 units, reorder at 10, takes 3 days to deliver.

---

### Function 2: `record_sale()` - Recording a Customer Purchase

**File:** `inventory.py`

**What it does:** Reduces stock by the quantity sold and logs the sale with today's date.

**Code:**
```python
def record_sale(item_id, qty, sale_date=None):
    if sale_date is None:
        sale_date = date.today()
    session = get_session()
    item = session.query(Item).filter(Item.id == item_id).first()
    if item:
        item.current_quantity -= qty
        sale_record = SalesHistory(item_id=item_id, date=sale_date, quantity_sold=-qty)
        session.add(sale_record)
        session.commit()
    session.close()
```

**Explanation:**
- `if sale_date is None: sale_date = date.today()` → If no date given, use today
- `session.query(Item).filter(Item.id == item_id).first()` → Find the item
- `item.current_quantity -= qty` → Subtract sold quantity from stock
- `SalesHistory(..., quantity_sold=-qty)` → Store negative number to identify as sale
- `session.commit()` → Save both stock update and sale record

**Example:** `record_sale(7, 5)` removes 5 units from item ID 7 and logs a sale.

---

### Function 3: `record_purchase()` - Receiving New Stock

**File:** `inventory.py`

**What it does:** Increases stock when new inventory arrives and logs the purchase.

**Code:**
```python
def record_purchase(item_id, qty, purchase_date=None):
    if purchase_date is None:
        purchase_date = date.today()
    session = get_session()
    item = session.query(Item).filter(Item.id == item_id).first()
    if item:
        item.current_quantity += qty
        purchase_record = SalesHistory(item_id=item_id, date=purchase_date, quantity_sold=qty)
        session.add(purchase_record)
        session.commit()
    session.close()
```

**Explanation:**
- `item.current_quantity += qty` → Add new stock to existing quantity
- `quantity_sold=qty` → Positive number identifies as purchase (not a sale)
- Rest is same as `record_sale()`

**Example:** `record_purchase(7, 20)` adds 20 units to item ID 7.

---

### Function 4: `get_all_items_df()` - Getting All Items as a Table

**File:** `inventory.py`

**What it does:** Retrieves all items from database and returns them as a table (DataFrame).

**Code:**
```python
def get_all_items_df():
    session = get_session()
    items = session.query(Item).all()
    df = pd.DataFrame([{
        'id': i.id, 
        'name': i.name, 
        'current_quantity': i.current_quantity,
        'reorder_point': i.reorder_point,
        'lead_time_days': i.lead_time_days
    } for i in items])
    session.close()
    return df
```

**Explanation:**
- `session.query(Item).all()` → Get every item from database
- `pd.DataFrame([{...} for i in items])` → Convert list of items into a table
- Returns table that Streamlit can display

**Example Output:**
| id | name | current_quantity | reorder_point | lead_time_days |
|----|------|------------------|---------------|----------------|
| 1 | Milk | 45 | 10 | 3 |
| 2 | Bread | 12 | 5 | 2 |

---

### Function 5: `forecast_depletion()` - Predicting When Stock Runs Out

**File:** `forecasting.py`

**What it does:** Uses past sales to predict future daily demand and calculate days until stockout.

**Code:**
```python
def forecast_depletion(item_id, forecast_days=30):
    history = get_daily_demand_history(item_id)
    
    if len(history) < 7:
        return {"error": "Insufficient history (need at least 7 days of data)"}
    
    df = get_all_items_df()
    item = df[df['id'] == item_id]
    current_qty = item.iloc[0]['current_quantity']
    
    try:
        model = SimpleExpSmoothing(history).fit(smoothing_level=0.3, optimized=True)
        forecast = model.forecast(forecast_days)
        daily_demand = max(forecast.mean(), 0.01)
    except:
        daily_demand = max(history.mean(), 0.01)
        forecast = pd.Series([daily_demand] * forecast_days)
    
    days_to_depletion = current_qty / daily_demand
    
    return {
        "predicted_daily_demand": round(float(daily_demand), 2),
        "days_until_stockout": round(days_to_depletion, 1),
        "forecast_values": forecast.tolist(),
        "model_used": "Exponential Smoothing"
    }
```

**Explanation:**
- `history = get_daily_demand_history(item_id)` → Get last 30 days of sales
- `if len(history) < 7` → Need at least 7 days to make prediction
- `SimpleExpSmoothing(history).fit()` → Apply exponential smoothing (math formula)
- `daily_demand = forecast.mean()` → Average predicted daily sales
- `days_to_depletion = current_qty / daily_demand` → Stock divided by daily demand
- Returns dictionary with predictions

**Example:** If stock = 100 and daily demand = 20 → stockout in 5 days

---

### Function 6: `check_alerts()` - Generating Warnings

**File:** `alerts.py`

**What it does:** Checks every item for low stock or predicted stockout and returns alert messages.

**Code:**
```python
def check_alerts():
    df = get_all_items_df()
    alerts = []
    
    for _, item in df.iterrows():
        # Check low stock alert
        if item['current_quantity'] <= item['reorder_point']:
            alerts.append(f"⚠️ LOW STOCK: {item['name']} has only {item['current_quantity']} left")
        
        # Check forecast alert
        forecast = forecast_depletion(item['id'])
        if 'error' not in forecast:
            days = forecast['days_until_stockout']
            lead_time = item['lead_time_days']
            if days <= lead_time:
                alerts.append(f"📉 PREDICTED STOCKOUT: {item['name']} will run out in {days} days")
    
    return alerts
```

**Explanation:**
- `df = get_all_items_df()` → Get all items
- `for _, item in df.iterrows()` → Loop through each item
- `if item['current_quantity'] <= item['reorder_point']` → Check low stock
- `forecast = forecast_depletion(item['id'])` → Get prediction
- `if days <= lead_time` → Check if stockout happens before new stock arrives
- Returns list of alert messages

**Example Output:** `["⚠️ LOW STOCK: Milk has 8 left", "📉 PREDICTED STOCKOUT: Bread will run out in 2 days"]`

---

### Function 7: `get_daily_demand_history()` - Preparing Sales Data for Forecasting

**File:** `forecasting.py`

**What it does:** Takes raw sales records and groups them by day for forecasting.

**Code:**
```python
def get_daily_demand_history(item_id):
    df = get_sales_history(item_id)
    if df.empty:
        return pd.Series([])
    
    sales_df = df.copy()
    sales_df['date'] = pd.to_datetime(sales_df['date'])
    daily = sales_df.groupby('date')['quantity_sold'].sum()
    return daily
```

**Explanation:**
- `df = get_sales_history(item_id)` → Get all sales records for this item
- `sales_df['date'] = pd.to_datetime(sales_df['date'])` → Convert to date format
- `groupby('date')['quantity_sold'].sum()` → Combine multiple sales on same day
- Returns daily totals ready for forecasting

**Example Input (raw):**
| date | quantity_sold |
|------|---------------|
| 2026-04-20 | 5 |
| 2026-04-20 | 3 |
| 2026-04-21 | 7 |

**Example Output (grouped):**
| date | quantity_sold |
|------|---------------|
| 2026-04-20 | 8 |
| 2026-04-21 | 7 |

---

## Part 3: How All Functions Work Together

### Data Flow Diagram

```
User clicks "Record Sale" in app.py
         ↓
app.py calls record_sale(item_id, 5)
         ↓
record_sale() updates current_quantity in items table
         ↓
record_sale() adds row to sales_history table
         ↓
Database now has updated stock + sale record
         ↓
User goes to Forecast page
         ↓
app.py calls forecast_depletion(item_id)
         ↓
forecast_depletion() calls get_daily_demand_history()
         ↓
get_daily_demand_history() queries sales_history table
         ↓
Returns daily sales totals
         ↓
Exponential Smoothing calculates daily demand
         ↓
Days until stockout = stock ÷ daily demand
         ↓
Results displayed in browser
         ↓
User sees: "Will run out in 5 days"
```

### Simple Analogy

| Component | Analogy |
|-----------|---------|
| `database.py` | Filing cabinet where all records are stored |
| `inventory.py` | Clerk who updates records when sales happen |
| `forecasting.py` | Calculator that looks at past sales to predict future |
| `alerts.py` | Manager who checks for problems and warns you |
| `app.py` | Reception desk where you see everything |

---

## Part 4: Testing Implementation

### Test Files Overview

| File | Test Type | What It Tests |
|------|-----------|---------------|
| `tests/test_crud.py` | Black-box | Add, sale, purchase, delete operations |
| `tests/test_forecasting.py` | White-box + Validation | Forecast logic + accuracy (MAE/RMSE) |
| `tests/test_stress.py` | Stress | Performance with 100 items, 3650 records |

---

### Black-Box Testing (`test_crud.py`)

**What it does:** Tests user actions without knowing internal code.

**Functions:**

```python
def test_add_item_blackbox(test_db):
    item_id = add_item("Test Laptop", 100.0, 25.0, 7)
    df = get_all_items_df()
    assert len(df) == 1
    assert df.iloc[0]['name'] == "Test Laptop"
```

**Explanation:** Adds an item, then checks if it appears in the database. Does not care how it works internally.

```python
def test_record_sale_blackbox(test_db):
    item_id = add_item("Test Mouse", 50.0)
    record_sale(item_id, 10.0)
    df = get_all_items_df()
    assert df.iloc[0]['current_quantity'] == 40.0
```

**Explanation:** Records a sale, then checks if stock decreased by the correct amount.

---

### White-Box Testing (`test_forecasting.py`)

**What it does:** Tests internal logic of forecasting functions.

```python
def test_forecast_whitebox_insufficient_data(test_db):
    item_id = add_item("Test Item", 100.0)
    result = forecast_depletion(item_id)
    assert "error" in result
```

**Explanation:** Tests that the function returns an error when there is not enough sales history.

```python
def test_forecast_whitebox_with_data(test_db):
    item_id = add_item("Constant Item", 200.0)
    for i in range(30):
        record_sale(item_id, 10.0, sale_date)
    result = forecast_depletion(item_id)
    assert result["predicted_daily_demand"] > 8
```

**Explanation:** Creates 30 days of constant sales (10 units/day), then checks that the forecast is close to 10.

---

### Validation Testing (inside `test_forecasting.py`)

**What it does:** Measures prediction accuracy using MAE and RMSE.

```python
def test_forecast_validation_accuracy(test_db):
    # Generate 60 days of sales
    for i in range(60):
        record_sale(item_id, qty, sale_date)
    
    # Split into train (50 days) and test (10 days)
    train = daily.iloc[:-10]
    test = daily.iloc[-10:]
    
    # Fit model on train, predict test
    model = SimpleExpSmoothing(train).fit()
    forecast = model.forecast(10)
    
    # Calculate errors
    mae = mean_absolute_error(test, forecast)
    rmse = np.sqrt(mean_squared_error(test, forecast))
    
    assert mae < 10.0
    assert rmse < 12.0
```

**Explanation:**
- Uses 50 days of data to predict the next 10 days
- Compares predictions to actual sales
- MAE = Average error (e.g., off by 3 units)
- RMSE = Penalizes large errors more
- Asserts errors are within acceptable range

---

### Stress Testing (`test_stress.py`)

**What it does:** Tests performance with large amounts of data.

```python
def test_stress_large_dataset(test_db):
    start_time = time.time()
    
    # Create 100 items
    for i in range(100):
        add_item(f"Stress Item {i}", 500.0)
    
    # Add 365 days of sales for first 10 items
    for item_id in item_ids[:10]:
        for day in range(365):
            record_sale(item_id, random.randint(5, 30), sale_date)
    
    load_time = time.time() - start_time
    assert load_time < 30.0
    
    df = get_all_items_df()
    assert len(df) == 100
```

**Explanation:**
- Creates 100 items and 3,650 sales records
- Measures time to create all data (<30 seconds)
- Measures time to load dashboard (<2 seconds)
- Ensures app remains responsive with large data

---

## Part 5: How Requirements Were Met

### Original Project Requirements

| Requirement | How Met | Evidence |
|-------------|---------|----------|
| Track inventory levels | Dashboard shows current_quantity for all items | `get_all_items_df()` returns table |
| Predict stock depletion | Exponential Smoothing calculates days until stockout | `forecast_depletion()` returns prediction |
| Trigger restock alerts | Alerts page shows LOW STOCK and PREDICTED STOCKOUT | `check_alerts()` returns warnings |
| CRUD operations | Add, delete, record sales, record purchases | `add_item()`, `delete_item()`, `record_sale()`, `record_purchase()` |
| Trend analysis | Line chart shows 30-day sales history | `get_daily_demand_history()` + `plotly.line()` |
| Automated notifications | In-app warnings using st.warning() | `st.warning(alert)` in Alerts page |

### Testing Requirements

| Requirement | How Met | Test File |
|-------------|---------|-----------|
| White-box testing | Tests internal forecast logic | `test_forecasting.py` |
| Black-box testing | Tests CRUD inputs/outputs | `test_crud.py` |
| Stress testing | Tests 100 items + 3650 records | `test_stress.py` |
| Validation testing | MAE/RMSE accuracy metrics | `test_forecasting.py` |

### Test Results

```
tests/test_crud.py::test_add_item_blackbox PASSED
tests/test_crud.py::test_record_sale_blackbox PASSED
tests/test_crud.py::test_record_purchase_blackbox PASSED
tests/test_crud.py::test_delete_item_blackbox PASSED
tests/test_forecasting.py::test_forecast_whitebox_insufficient_data PASSED
tests/test_forecasting.py::test_forecast_whitebox_with_data PASSED
tests/test_forecasting.py::test_forecast_validation_accuracy PASSED
tests/test_stress.py::test_stress_large_dataset PASSED
```

**8/8 tests passed (100%)**

---

## Part 6: File Structure

```
smart-invento-app/
├── app.py                 (User interface)
├── database.py            (Database setup)
├── inventory.py           (CRUD operations)
├── forecasting.py         (Predictions)
├── alerts.py              (Warnings)
├── inventory.db           (Database file - auto-generated)
├── requirements.txt       (Packages)
├── tests/
│   ├── __init__.py
│   ├── conftest.py        (Test database fixture)
│   ├── test_crud.py       (Black-box tests)
│   ├── test_forecasting.py (White-box + validation)
│   └── test_stress.py     (Stress tests)
└── venv/                  (Virtual environment)
```

---

## Conclusion

This application successfully meets all project requirements:

✅ Tracks inventory with full CRUD operations  
✅ Predicts stock depletion using Exponential Smoothing  
✅ Triggers automatic restocking alerts  
✅ Provides trend analysis with interactive charts  
✅ Implements white-box, black-box, stress, and validation testing  
✅ All 8 tests pass (100%)

**The application is complete and ready for submission.**