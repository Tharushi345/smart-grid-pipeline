import random
import psycopg2

HOUSEHOLDS = [f"H{i:03d}" for i in range(1, 21)]

conn = psycopg2.connect(
    dbname="griddb",
    user="grid",
    password="grid",
    host="localhost"
)

cur = conn.cursor()

cur.execute(
    "DELETE FROM tariff_billing_daily WHERE day = CURRENT_DATE"
)

for h in HOUSEHOLDS:
    cur.execute(
        "INSERT INTO tariff_billing_daily "
        "(household_id, tariff_rate, billing_tier, subsidy_flag) "
        "VALUES (%s,%s,%s,%s)",
        (
            h,
            round(random.uniform(15, 35), 2),
            random.choice(["standard", "premium"]),
            random.random() < 0.2
        )
    )

conn.commit()
conn.close()

print("tariff data for", len(HOUSEHOLDS), "households written")