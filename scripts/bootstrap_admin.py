import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import select

from database.schema.user_schema import UserSchema
from utils.data_base_engine import SessionLocal


def main() -> None:
    parser = argparse.ArgumentParser(description="Promote an existing user to the initial administrator role.")
    parser.add_argument("username")
    args = parser.parse_args()

    database = SessionLocal()
    try:
        user = database.scalar(select(UserSchema).where(UserSchema.username == args.username))
        if not user:
            raise SystemExit(f"User not found: {args.username}")
        user.user_type = "admin"
        user.restaurant_id = None
        database.commit()
        print(f"Administrator configured: {user.username}")
    finally:
        database.close()


if __name__ == "__main__":
    main()
