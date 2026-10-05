"""Validate the schemas, the examples, and cases the schemas must reject.

Run: python3 tools/check_schemas.py  (needs jsonschema >= 4.18)
"""
import copy
import json
import pathlib
import sys

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCHEMAS = ROOT / "schemas"


def load(path):
    return json.loads(path.read_text())


def validator(name):
    schema = load(SCHEMAS / name)
    jsonschema.Draft202012Validator.check_schema(schema)
    return jsonschema.Draft202012Validator(schema, format_checker=jsonschema.FormatChecker())


def main():
    failures = 0
    for path in sorted(SCHEMAS.glob("*.schema.json")):
        validator(path.name)
        print(f"schema ok    {path.name}")

    record = validator("evaluation-record.schema.json")
    for path in sorted((SCHEMAS / "examples").glob("*.json")):
        errors = list(record.iter_errors(load(path)))
        print(f"{'example ok ' if not errors else 'EXAMPLE BAD'}  {path.name}")
        for err in errors:
            print("   ", err.message[:200], list(err.path))
        failures += len(errors)

    base = load(SCHEMAS / "examples" / "evaluation-record.example.json")
    must_reject = {
        "MEASURED value below stable maturity": lambda r: r["values"][1].update(evidence_class="MEASURED"),
        "ok value without value field": lambda r: r["values"][0].pop("value"),
        "abstained value carrying a value": lambda r: r["values"][3].update(value=1),
        "value without confidence field": lambda r: r["values"][0].pop("confidence"),
        "ESTIMATED ok value with null confidence": lambda r: r["values"][0].update(confidence=None),
        "PROXY without .proxy metric id": lambda r: r["values"][4].update(metric_id="groove.head_nod"),
        "non-proxy value with proxy_for": lambda r: r["values"][0].update(proxy_for="groove.pocket"),
        "EAR value without capture": lambda r: r["values"][5].pop("capture"),
        "station capture without normalization": lambda r: r["values"][5]["capture"].pop("normalization"),
        "BUILD with four criteria": lambda r: r["composites"]["build"]["criteria"].pop(),
        "FEEL id inside BUILD": lambda r: r["composites"]["build"]["criteria"][0].update(id="F1"),
        "FEEL result inside BUILD": lambda r: r["composites"]["build"]["criteria"][0].update(result="detected"),
        "record with both asset and external": lambda r: r.update(external={"spotify_uri": "spotify:track:" + "a" * 22}),
        "created_at with non-UTC offset": lambda r: r.update(created_at="2026-10-05T18:40:00+05:00"),
        "asset record without engine": lambda r: r.pop("engine"),
        "source label with hyphen": lambda r: r["asset"].update(source="cd-rip"),
    }
    for desc, mutate in must_reject.items():
        candidate = copy.deepcopy(base)
        mutate(candidate)
        rejected = bool(list(record.iter_errors(candidate)))
        print(f"{'rejects ok ' if rejected else 'NOT REJECTED'}  {desc}")
        failures += 0 if rejected else 1

    print("FAIL" if failures else "PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
