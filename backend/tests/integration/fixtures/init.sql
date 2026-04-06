DROP TABLE IF EXISTS anomalies;
DROP TABLE IF EXISTS audits;
DROP TABLE IF EXISTS listings;
DROP TABLE IF EXISTS properties;

CREATE TABLE properties (
    id UUID PRIMARY KEY,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(100) NOT NULL,
    zip_code VARCHAR(20) NOT NULL,
    property_type VARCHAR(50) NOT NULL,
    bedrooms INTEGER,
    bathrooms INTEGER,
    square_meters DOUBLE PRECISION,
    year_built INTEGER
);

CREATE TABLE listings (
    id UUID PRIMARY KEY,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    asking_price NUMERIC(15, 2) NOT NULL,
    status VARCHAR(50) NOT NULL,
    listed_date TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE audits (
    id UUID PRIMARY KEY,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    estimated_rental_income NUMERIC(12, 2),
    estimated_maintenance_costs NUMERIC(12, 2),
    gross_yield_percentage DOUBLE PRECISION,
    calculated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE anomalies (
    id UUID PRIMARY KEY,
    property_id UUID NOT NULL REFERENCES properties(id) ON DELETE CASCADE,
    flag_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    severity VARCHAR(20) NOT NULL
);

CREATE INDEX idx_properties_city ON properties(city);
CREATE INDEX idx_listings_status ON listings(status);

INSERT INTO properties (id, address, city, zip_code, property_type, bedrooms, bathrooms, square_meters, year_built)
VALUES
    ('11111111-1111-1111-1111-111111111111', '12 Rue de Rivoli', 'Paris', '75004', 'apartment', 2, 1, 73.0, 1890),
    ('22222222-2222-2222-2222-222222222222', '18 Rue Saint-Antoine', 'Paris', '75004', 'apartment', 2, 1, 70.0, 1905),
    ('33333333-3333-3333-3333-333333333333', '5 Boulevard Beaumarchais', 'Paris', '75004', 'apartment', 3, 2, 85.0, 1910),
    ('44444444-4444-4444-4444-444444444444', '8 Avenue Jean Jaures', 'Lyon', '69006', 'apartment', 2, 1, 55.0, 1975);

INSERT INTO listings (id, property_id, asking_price, status)
VALUES
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa1', '11111111-1111-1111-1111-111111111111', 820000.00, 'active'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa2', '22222222-2222-2222-2222-222222222222', 1100000.00, 'active'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa3', '33333333-3333-3333-3333-333333333333', 1250000.00, 'active'),
    ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaa4', '44444444-4444-4444-4444-444444444444', 310000.00, 'active');

INSERT INTO audits (id, property_id, estimated_rental_income, estimated_maintenance_costs, gross_yield_percentage)
VALUES
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb1', '11111111-1111-1111-1111-111111111111', 28372.00, 4100.00, 3.46),
    ('bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbb4', '44444444-4444-4444-4444-444444444444', 15900.00, 2500.00, 5.13);

INSERT INTO anomalies (id, property_id, flag_type, description, severity)
VALUES
    ('cccccccc-cccc-cccc-cccc-ccccccccccc1', '11111111-1111-1111-1111-111111111111', 'Low Yield', 'Yield below 4.6%', 'Medium'),
    ('cccccccc-cccc-cccc-cccc-ccccccccccc2', '11111111-1111-1111-1111-111111111111', 'Suspiciously Cheap', 'Price per sqm 11232.88 is far below peer average 15210.08 in zip 75004', 'High');
