import argparse
import json
import sys
from .validation import Invalid, read_json, validate, verify_package
from .m1 import gate0, dataset_fingerprint, verify_upstream
from .m3 import audit_backup

def main():
    parser = argparse.ArgumentParser(description="WDFG M0 local validation; no inference")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("verify-package")
    p.add_argument("package")
    p = sub.add_parser("validate-config")
    p.add_argument("config")
    p.add_argument("--package", required=True)
    p = sub.add_parser("gate0-fixture")
    p.add_argument("evidence")
    p = sub.add_parser("fingerprint-dataset")
    p.add_argument("records")
    p.add_argument("--preprocessing-version", required=True)
    p = sub.add_parser("backup-fixture")
    p.add_argument("evidence")
    sub.add_parser("verify-upstream")
    args = parser.parse_args()
    try:
        if args.command == "backup-fixture":
            result = audit_backup(read_json(args.evidence))
        elif args.command == "gate0-fixture":
            result = gate0(read_json(args.evidence))
        elif args.command == "fingerprint-dataset":
            result = dataset_fingerprint(read_json(args.records), args.preprocessing_version)
        elif args.command == "verify-upstream":
            result = {"validation_status": "PASS", **verify_upstream()}
        elif args.command == "verify-package":
            baseline, count = verify_package(args.package)
            result = {"validation_status": "PASS", "validated_payload_files": count, **baseline}
        else:
            result = validate(read_json(args.config), args.package)
        print(json.dumps(result, indent=2))
        return 0
    except (Invalid, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"validation_status": "FAIL", "error": str(exc)}), file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
