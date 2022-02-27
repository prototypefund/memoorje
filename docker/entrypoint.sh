#!/bin/sh

set -eu
if [ -z "${NO_EXECUTE_MIGRATIONS:-}" ]; then
  python3 -m django migrate --noinput
fi
if [ "${MEMOORJE_LOAD_TEST_FIXTURES:-0}" = "1" ]; then
  python3 -m django loaddata /app/fixtures.json
fi
exec "$@"
