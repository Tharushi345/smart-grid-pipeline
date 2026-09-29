from fastapi import FastAPI
import psycopg2
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("serving")


def db():
    return psycopg2.connect(
        dbname="griddb",
        user="grid",
        password="grid",
        host="localhost"
    )


@app.get("/realtime/zones")
def zones():
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT DISTINCT ON (grid_zone)
            grid_zone,
            total_consumption,
            total_solar,
            renewable_pct
        FROM zone_realtime_metrics
        ORDER BY grid_zone, window_start DESC
        """
    )

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "zone": r[0],
            "consumption": r[1],
            "solar": r[2],
            "renewable_pct": r[3]
        }
        for r in rows
    ]


@app.get("/billing/{household_id}")
def billing(household_id: str):
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT day, bill
        FROM daily_billing_report
        WHERE household_id=%s
        ORDER BY day DESC
        LIMIT 1
        """,
        (household_id,)
    )

    row = cur.fetchone()
    conn.close()

    if row:
        return {
            "household_id": household_id,
            "day": str(row[0]),
            "bill": row[1]
        }

    return {"error": "not found"}


@app.get("/alerts")
def alerts():
    conn = db()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT level, message, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 20
        """
    )

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "level": r[0],
            "message": r[1],
            "time": str(r[2])
        }
        for r in rows
    ]


@app.get("/health")
def health():
    return {"status": "ok"}