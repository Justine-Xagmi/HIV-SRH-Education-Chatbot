
from sqlalchemy import text

from app.db.session import SessionLocal


def main() -> None:
    if SessionLocal is None:
        print("FAIL: DATABASE_URL is not configured.")
        return

    db = SessionLocal()

    try:
        query = text(
            """
            SELECT
                t.tgname,
                t.tgenabled,
                c.relname AS table_name,
                n.nspname AS schema_name,
                p.proname AS function_name,
                pg_get_triggerdef(t.oid) AS trigger_definition
            FROM pg_trigger AS t
            JOIN pg_class AS c
                ON c.oid = t.tgrelid
            JOIN pg_namespace AS n
                ON n.oid = c.relnamespace
            JOIN pg_proc AS p
                ON p.oid = t.tgfoid
            WHERE t.tgname = :trigger_name
              AND NOT t.tgisinternal;
            """
        )

        result = db.execute(
            query,
            {"trigger_name": "trg_document_versions_immutable"},
        ).mappings().first()

        if result is None:
            print("FAIL: Immutability trigger is missing.")
            return

        print("Trigger verification details:")
        print(f"  Trigger: {result['tgname']}")
        print(f"  Schema: {result['schema_name']}")
        print(f"  Table: {result['table_name']}")
        print(f"  Function: {result['function_name']}")
        print(f"  Enabled status: {result['tgenabled']}")
        print(f"  Definition: {result['trigger_definition']}")

        checks = {
            "Correct table": result["table_name"] == "document_versions",
            "Correct function": (
                result["function_name"]
                == "prevent_document_version_mutation"
            ),
            "Enabled": result["tgenabled"] in ("O", "A"),
        }

        print("\nVerification results:")

        for check, passed in checks.items():
            print(f"  {'PASS' if passed else 'FAIL'}: {check}")

        if all(checks.values()):
            print(
                "\nPASS: Document-version immutability "
                "trigger is correctly installed and enabled."
            )
        else:
            print(
                "\nFAIL: Document-version immutability "
                "trigger requires attention."
            )

    except Exception as exc:
        print(f"Database verification failed: {exc}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
