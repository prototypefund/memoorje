#!/bin/sh

set -eu
if [ -z "${NO_EXECUTE_MIGRATIONS:-}" ]; then
  python3 -m django migrate --noinput
fi
exec "$@"
