"""Fail-closed local validation. Never executes package instructions."""
import hashlib
import json
from pathlib import Path, PurePosixPath
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent / "resources"

class Invalid(ValueError):
    pass

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise Invalid(f"Duplicate JSON key: {key}")
            result[key] = value
        return result
    return json.loads(Path(path).read_text(), object_pairs_hook=unique,
                      parse_constant=lambda x: (_ for _ in ()).throw(Invalid(f"Invalid number: {x}")))

def check_schema(value, name):
    schema = read_json(ROOT / "schemas" / name)
    Draft202012Validator.check_schema(schema)
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda e: str(e.path))
    if errors:
        raise Invalid("; ".join(e.message for e in errors))

def verify_package(directory):
    directory = Path(directory).resolve()
    baseline = read_json(ROOT / "baseline.json")
    raw = (directory / "manifest.json").read_bytes()
    if digest(raw) != baseline["package_manifest_sha256"]:
        raise Invalid("Package manifest differs from pinned M0 baseline")
    manifest = read_json(directory / "manifest.json")
    seen = set()
    for entry in manifest["files"]:
        name = entry["path"]
        rel = PurePosixPath(name)
        if rel.is_absolute() or ".." in rel.parts or name in seen:
            raise Invalid("Unsafe or duplicate manifest path")
        seen.add(name)
        path = directory / name
        if path.is_symlink() or not path.resolve().is_relative_to(directory):
            raise Invalid("Artifact escapes package")
        raw = path.read_bytes()
        if len(raw) != entry["bytes"] or digest(raw) != entry["sha256"]:
            raise Invalid(f"Artifact mismatch: {name}")
    actual = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
    if actual != seen | {"manifest.json"}:
        raise Invalid("Package has unmanifested or missing files")
    if digest((directory / baseline["protocol_path"]).read_bytes()) != baseline["protocol_sha256"]:
        raise Invalid("Protocol mismatch")
    return baseline, len(seen)

def validate(config, directory):
    check_schema(config, "config.schema.json")
    baseline, count = verify_package(directory)
    for key in ("protocol_sha256", "package_manifest_sha256"):
        if config[key] != baseline[key]:
            raise Invalid(f"Config {key} does not match verified package")
    if (config["freeze_status"] == "frozen") != (not config["open_freezes"]):
        raise Invalid("Freeze status contradicts open-freeze list")
    params = config["scientific_parameters"]
    required = {"P1": ("coefficient_threshold", "alpha"),
                "P2": ("mask_sha256", "candidate_pool_sha256", "paired_power_method"),
                "P3": ("K", "B", "regime", "decoding", "precision_receipt_sha256"),
                "P4": ("optimizer", "learning_rate", "token_budget", "checkpoint_schedule")}
    if any(key not in params or params[key] is None for key in required[config["stage"]]):
        raise Invalid("Missing explicit scientific parameters for stage")
    if config["stage"] == "P1":
        if type(params["coefficient_threshold"]) not in (int, float) or params["coefficient_threshold"] not in (0.0005, 0.001, 0.002):
            raise Invalid("Invalid coefficient threshold")
        if type(params["alpha"]) not in (int, float) or params["alpha"] not in (0.0, 0.5):
            raise Invalid("Invalid suppression alpha")
    if config["stage"] == "P3":
        if any(type(params[x]) is not int or params[x] <= 0 for x in ("K", "B")):
            raise Invalid("K and B must be explicit positive integers")
        if params["regime"] not in ("I0", "I0b", "I1", "I2"):
            raise Invalid("Unknown continuation regime")
    if config["run_kind"] != "fixture":
        if config["data_kind"] == "synthetic":
            raise Invalid("Synthetic fixtures cannot become pilot or result data")
        if config["freeze_status"] != "frozen":
            raise Invalid("Empirical stages require closed freezes")
        # M0 has no dataset/upstream receipt verifier or model contract yet.
        # Relabelling JSON is never sufficient to establish empirical provenance.
        raise Invalid("Empirical provenance verification is not implemented in M0")
    if config["data_kind"] != "synthetic":
        raise Invalid("M0 fixture mode requires explicitly synthetic data")
    receipt = {"schema_version": "wdfg.validation-receipt/0.1",
               "run_kind": config["run_kind"], **{k:baseline[k] for k in ("protocol_sha256", "package_manifest_sha256")},
               "config_sha256": digest(json.dumps(config, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()),
               "freeze_status": config["freeze_status"], "open_freezes": config["open_freezes"],
               "validation_status": "PASS", "scientific_status": "NOT_EVALUATED",
               "execution_authorized": False, "validated_payload_files": count}
    check_schema(receipt, "run_manifest.schema.json")
    return receipt
