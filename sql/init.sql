CREATE TABLE zone_realtime_metrics (
  grid_zone TEXT,
  window_start TIMESTAMP,
  total_consumption FLOAT,
  total_solar FLOAT,
  renewable_pct FLOAT,
  PRIMARY KEY (grid_zone, window_start)
);

CREATE TABLE raw_readings (
  meter_id TEXT,
  household_id TEXT,
  power_consumption_kwh FLOAT,
  solar_generation_kwh FLOAT,
  grid_zone TEXT,
  ts TIMESTAMP
);

CREATE TABLE tariff_billing_daily (
  household_id TEXT,
  tariff_rate FLOAT,
  billing_tier TEXT,
  subsidy_flag BOOLEAN,
  day DATE DEFAULT CURRENT_DATE
);

CREATE TABLE daily_billing_report (
  household_id TEXT,
  day DATE,
  net_consumption FLOAT,
  tariff_rate FLOAT,
  bill FLOAT,
  PRIMARY KEY (household_id, day)
);

CREATE TABLE alerts (
  id SERIAL PRIMARY KEY,
  level TEXT,
  message TEXT,
  created_at TIMESTAMP DEFAULT now()
);