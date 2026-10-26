
from sqlalchemy import text
from app.db.session import SessionLocal


def main():
    if SessionLocal is None:
        print("FAIL: DATABASE_URL is not configured.")
        return

    db = SessionLocal()

    try:
        query = text("""
            SELECT EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgname = 'trg_document_versions_immutable'
                  AND NOT tgisinternal
            )
        """)

        trigger_exists = db.scalar(query)

        print(f"Immutability trigger exists: {trigger_exists}")

        if trigger_exists:
            print("PASS: Document-version immutability trigger is installed.")
        else:
            print("FAIL: Document-version immutability trigger is missing.")

    except Exception as exc:
        print(f"Database verification failed: {exc}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
