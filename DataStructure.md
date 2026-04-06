# Data Structure
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
