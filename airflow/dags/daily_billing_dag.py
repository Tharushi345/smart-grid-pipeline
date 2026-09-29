from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import psycopg2


def get_conn():
    return psycopg2.connect(
        dbname="griddb",
        user="grid",
        password="grid",
        host="localhost"
    )


def run_billing():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO daily_billing_report
        SELECT
            r.household_id,
            CURRENT_DATE,
            GREATEST(
                SUM(r.power_consumption_kwh)
                - SUM(r.solar_generation_kwh),
                0
            ),
            t.tariff_rate,
            GREATEST(
                SUM(r.power_consumption_kwh)
                - SUM(r.solar_generation_kwh),
                0
            )
            * t.tariff_rate
            * CASE
                WHEN t.subsidy_flag THEN 0.8
                ELSE 1
              END
        FROM raw_readings r
        JOIN tariff_billing_daily t
        ON r.household_id = t.household_id
        GROUP BY
            r.household_id,
            t.tariff_rate,
            t.subsidy_flag
        ON CONFLICT (household_id, day)
        DO NOTHING
    """)

    conn.commit()
    conn.close()


def check_alerts():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT grid_zone, renewable_pct
        FROM zone_realtime_metrics
        WHERE window_start > now() - interval '5 minutes'
        AND renewable_pct < 0.15
    """)

    for zone, pct in cur.fetchall():
        cur.execute(
            "INSERT INTO alerts (level, message) VALUES (%s,%s)",
            (
                "WARNING",
                f"Low renewable contribution in {zone}: {pct:.0%}"
            )
        )

    conn.commit()
    conn.close()


with DAG(
    "daily_billing_dag",
    start_date=datetime(2026, 1, 1),
    schedule_interval="@daily",
    catchup=False
) as dag:

    t1 = PythonOperator(
        task_id="run_billing",
        python_callable=run_billing
    )

    t2 = PythonOperator(
        task_id="check_alerts",
        python_callable=check_alerts
    )

    t1 >> t2