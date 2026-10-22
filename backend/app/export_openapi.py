"""Prints the OpenAPI schema; `make types` turns it into the frontend's TypeScript types."""

import json
import sys

from app.main import create_app
from app.settings import Settings


def main() -> None:
    # Fixed settings: the schema must not depend on whatever is in a developer's .env.
    app = create_app(Settings(_env_file=None))
    sys.stdout.write(json.dumps(app.openapi(), indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
