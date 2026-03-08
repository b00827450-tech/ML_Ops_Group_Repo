# Project Structure
(Name your branch  dev_<function_name>, e.g. dev_search)  
## to do :
**important: keep it simple**

### 1. The Search Function
* **What you do:**  three box in fastAPI UI: city, price range min and max. type in the infomation.
* **What the script does:** backend code read from what u typed and fetch data from database and show related info.

### 2. The Property Audit

* **What you do:** type on ui a Property ID and your best guesses for monthly rent and yearly maintenance costs.
* **What the script does:** It grabs the home's current asking price, crunches the math to find your **Return on Investment (Gross Yield %)**, saves that report to database, and shows the final number.

### 3. Anomaly Detection (The Red Flags)

* **What you do:** type on ui to tell it to scan a specific property.
* **What the script does:** It calculates the price-per-square-meter for that home, then compares it to the average price of *every other similar home in that exact zip code*. If it's suspiciously cheap, wildly overpriced, or missing basic info (like 0 bathrooms), it slaps a "Red Flag" warning on it.


## development folder
 database.py  --defined a py file to connect to our database
 models.py    --define our tables to classes so that python can easily consume
 test.ipynb   --check how to consume our data


## Data Structure
1. **properties Table** (The Parent)
- id: UUID [Primary Key] (Auto-generates via uuid4)
- address: VARCHAR(255) [Not Null]
- city: VARCHAR(100) [Not Null] [Indexed for fast - searching]
- zip_code: VARCHAR(20) [Not Null]
- property_type: VARCHAR(50) [Not Null]
- bedrooms: INTEGER
- bathrooms: INTEGER
- square_meters: FLOAT
- year_built: INTEGER
- Relationships: Cascades deletes to listings, audits, - and anomalies.

2. **listings Table** (Child of Properties)
- id: UUID [Primary Key]
- property_id: UUID [Foreign Key -> properties.id] [ON - DELETE CASCADE]
- asking_price: NUMERIC(15, 2) [Not Null]
- status: VARCHAR(50) [Not Null] [Indexed]
- listed_date: DATETIME (Timezone aware) [Default: - Current server time]

3. **audits Table** (Child of Properties)
- id: UUID [Primary Key]
- property_id: UUID [Foreign Key -> properties.id] [ON - DELETE CASCADE]
- estimated_rental_income: NUMERIC(12, 2)
- estimated_maintenance_costs: NUMERIC(12, 2)
- gross_yield_percentage: FLOAT
- calculated_at: DATETIME (Timezone aware) [Default: - Current server time]

4. **anomalies Table** (Child of Properties)
- id: UUID [Primary Key]
- property_id: UUID [Foreign Key -> properties.id] [ON - DELETE CASCADE]
- flag_type: VARCHAR(100) [Not Null]
- description: TEXT [Not Null]
- severity: VARCHAR(20) [Not Null]

## Usefule git commands

**important: work on your own branch.**

```bash
git clone <repository_url>
```

**2. Pull Latest Changes** 

```bash
git pull origin <branch_name>
```

**3. Add Changes**

```bash
git add .
```

(or specify files)

```bash
git add <file_name>
```


**4. Commit Changes**

```bash
git commit -m "commit message"
```

**5. Push Changes**

```bash
git push origin <branch_name>
```

Example:

```bash
git push origin main
```

**6. Create Branch**
```
git branch <branch_name>
```

**7. Switch Branch**
```
git checkout <branch_name>
```
