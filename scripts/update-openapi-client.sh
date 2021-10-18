#!/bin/sh

set -eu

EXPORT_PATH=libjs/api
open_api_schema_file=$(mktemp)
trap 'rm -f "$open_api_schema_file"' EXIT
curl -sS --fail http://localhost:8000/api/schema/ >"$open_api_schema_file"
rm -rf "${EXPORT_PATH:?}/"
openapi-generator generate \
  -i "$open_api_schema_file" \
  -g typescript-fetch \
  -o "$EXPORT_PATH/" \
  --additional-properties npmName=@memoorje/api,supportsES6=true
  "$@"
find "$EXPORT_PATH/src/apis" -name "*.ts" | while read -r filename; do
  # some of the files contain a weird transformation to Blob types that we
  #   a) don’t need (and is not accepted by the backend) and
  #   b) produces invalid code because the stringToJSON method is missing
  sed -Ei 's|new Blob\(\[JSON\.stringify\(stringToJSON\(([^\)]+)\)\)\], \{ type: "application/json", \}\)|\1 as any|' "$filename"
done
# The generator creates an invalid type for the FetchAPI that we need to fix afterwards
sed -Ei "s|export type FetchAPI = .+;|export declare type FetchAPI = WindowOrWorkerGlobalScope['fetch'];|" "$EXPORT_PATH/src/runtime.ts"
# make sure the TypeScript config uses a recent EcmaScript target as target and the EcmaScript module system
jq '.compilerOptions.target = "es2020" | .compilerOptions.module = "esnext"' "$EXPORT_PATH/tsconfig.json" \
  | sponge "$EXPORT_PATH/tsconfig.json"
