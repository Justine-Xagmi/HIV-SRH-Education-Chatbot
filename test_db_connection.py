
from sqlalchemy import text

from app.db.session import engine


def main() -> None:
    if engine is None:
        raise RuntimeError(
            "Database URL is not configured. Check your local .env file."
        )

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_user, current_database(), version()")
        )
        row = result.fetchone()

        print("Database connection successful.")
        print("Current user:", row[0])
        print("Current database:", row[1])
        print("PostgreSQL version:", row[2].split(",")[0])


if __name__ == "__main__":
    main()
