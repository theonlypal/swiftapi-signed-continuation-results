"""Verify sealed evidence with the installed SwiftAPI SDK, without model inference."""
import argparse
from collections import Counter, defaultdict
import hashlib
from importlib.metadata import version
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import tarfile
import tempfile

from swiftapi.native_verify import read_json, verify_receipt

ROOT = Path(__file__).resolve().parent
MODE = 'FRESH_MODEL_EXECUTION'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def safe_name(name):
    path = PurePosixPath(name)
    require(name and '\\' not in name and not path.is_absolute()
            and '..' not in path.parts and str(path) == name,
            'Unsafe archive path')
    return path


def extract_archive(archive, destination, expected):
    require(archive.stat().st_size == expected['bytes'], 'Archive size mismatch')
    require(digest(archive) == expected['sha256'], 'Archive SHA-256 mismatch')
    with tarfile.open(archive, 'r:gz') as source:
        members = source.getmembers()
        require(len(members) <= 20000 and sum(m.size for m in members) <= 1_000_000_000,
                'Archive size limit')
        names = set()
        for member in members:
            require(member.isfile() and not member.issym() and not member.islnk(),
                    'Archive requires regular files')
            path = safe_name(member.name)
            require(member.name not in names, 'Duplicate archive member')
            names.add(member.name)
            target = destination / path
            target.parent.mkdir(parents=True, exist_ok=True)
            with source.extractfile(member) as stream, target.open('xb') as output:
                shutil.copyfileobj(stream, output)
    require(digest(destination / 'SHA256SUMS') == expected['manifest_sha256'],
            'Run manifest SHA-256 mismatch')
    listed = set()
    for line in (destination / 'SHA256SUMS').read_text().splitlines():
        match = re.fullmatch(r'([0-9a-f]{64})  (.+)', line)
        require(match is not None, 'Invalid manifest line')
        wanted, name = match.groups()
        safe_name(name)
        require(name not in listed and name in names, 'Manifest path mismatch')
        listed.add(name)
        require(digest(destination / name) == wanted, 'Manifest content mismatch: ' + name)
    require(listed == names - {'SHA256SUMS'}, 'Manifest coverage mismatch')
    return len(names)


def sealed_predictions(path, anchors):
    require(digest(path) == anchors['author_predictions_sha256'], 'Prediction seal mismatch')
    model = re.escape(anchors['model_identifier'])
    pattern = re.compile(r'`\[([A-Z_]+)\] \[' + model + r'\] \[([0-9]+)/([0-9]+)\] \[([A-Za-z0-9]+)\]`')
    predictions = {'PRIMARY': {}, 'SECONDARY': {}}
    current = None
    for line in path.read_text().splitlines():
        if line == '## Run 1: PRIMARY WITNESS_ONE':
            current = 'PRIMARY'
        elif line == '## Run 2: SECONDARY BANK_188':
            current = 'SECONDARY'
        elif line.startswith('`['):
            match = pattern.fullmatch(line)
            require(match is not None and current is not None, 'Prediction line mismatch')
            arm, count, total, cls = match.groups()
            require(int(count) == int(total) == (1 if current == 'PRIMARY' else 188),
                    'Prediction denominator mismatch')
            require(arm not in predictions[current], 'Duplicate prediction arm')
            predictions[current][arm] = {'class_counts': {cls: int(count)}}
    require(len(predictions['PRIMARY']) == 11 and len(predictions['SECONDARY']) == 2,
            'Prediction population mismatch')
    return predictions


def verify_finalization(root, config, count):
    record = read_json(root / 'mac-ledger-finalization.json')
    for field, name in (('before_sha256', 'mac-ledger-before.json'),
                        ('after_sha256', 'mac-ledger-after.json'),
                        ('reconciliation_sha256', 'authority-ledger-reconciliation.json')):
        require(record[field] == digest(root / name), 'Ledger finalization hash mismatch')
    canonical = json.dumps(config, sort_keys=True, separators=(',', ':'),
                           ensure_ascii=True, allow_nan=False).encode()
    require(record['config_sha256'] == hashlib.sha256(canonical).hexdigest(),
            'Ledger configuration hash mismatch')
    require(record['verified_receipts'] == count, 'Ledger receipt count mismatch')
    return record


def verify_run(root, run, expected, anchors):
    config = read_json(root / 'run-config.json')
    require(config['run_role'] == run and config['mode'] == MODE
            and config['purpose'] == 'PREREGISTERED_STUDY'
            and config['authority'] == 'LIVE_SWIFTAPI', 'Run identity mismatch')
    key = anchors['runtime_public_keys'][run]
    require(read_json(root / 'runtime-public.json')['public_key'] == key
            and config['runtime_public_key'] == key, 'Runtime trust anchor mismatch')
    require(read_json(root / 'authority-public.json')['public_key'] == anchors['authority_public_key']
            and config['authority_public_key'] == anchors['authority_public_key'], 'Authority trust anchor mismatch')
    require(config['service_source_sha256'] == anchors['service_source_sha256']
            and config['classifier_sha256'] == anchors['classifier_sha256']
            and config['max_grant_age_seconds'] == anchors['expected_max_grant_age_seconds'],
            'Registered source or policy mismatch')
    predictions = sealed_predictions(root / 'sealed-predictions.md', anchors)[run]
    require(config['predictions'] == predictions, 'Configuration predictions differ from sealed bytes')
    summary = read_json(root / 'summary.json')
    rows = summary['rows']
    total = 1 if run == 'PRIMARY' else 188
    schedule = config['schedule']
    require(set(schedule) == set(predictions) and len(schedule) == len(predictions), 'Arm schedule mismatch')
    slots = [(qi, arm) for qi in range(total) for arm in schedule]
    require(len(rows) == len(slots) == expected['receipt_count'] == summary['planned_count'],
            'Receipt denominator mismatch')
    counts, executions, paths = defaultdict(Counter), set(), set()
    model_receipts = 0
    for index, (row, (qi, arm)) in enumerate(zip(rows, slots)):
        name = f'receipts/{index:04}-{arm}/receipt.json'
        require(row['slot'] == index and row['question_index'] == qi
                and row['arm'] == arm and row['receipt'] == name, 'Slot mapping mismatch')
        path = root / name
        payload = read_json(path)['payload']
        require(payload['purpose'] == 'PREREGISTERED_STUDY', 'Receipt purpose mismatch')
        require(payload['execution_id'] not in executions, 'Duplicate execution identity')
        executions.add(payload['execution_id'])
        paths.add(name)
        report = verify_receipt(path, key, MODE,
                                authority_key=anchors['authority_public_key'],
                                expected_source_sha256=anchors['service_source_sha256'],
                                expected_max_grant_age_seconds=anchors['expected_max_grant_age_seconds'])
        require(payload['taxonomy']['classifier_sha256'] == anchors['classifier_sha256'],
                'Classifier pin mismatch')
        result = payload.get('result') or {}
        observation = {'class': report['class'], 'output_bytes': len(payload['output'].encode('utf-8')),
                       'first_token': (result.get('generated_token_ids') or [None])[0],
                       'generation_complete': result.get('generation_complete')}
        require(row['observation'] == observation and row['class'] == report['class'],
                'Summary differs from signed receipt')
        if payload.get('action') is not None:
            profile = payload['action']['profile']
            require(profile['repository'] + '@' + profile['revision'] == anchors['model_identifier'],
                    'Model identity mismatch')
            require(all(profile[name] == value for name, value in config['pins'].items()),
                    'Model input pin mismatch')
            require(payload['action']['request']['question'] == row['question'], 'Question binding mismatch')
        if report['class'] != 'operational':
            require(report['non_eos_unchanged'] is True, 'Non-EOS identity mismatch')
            model_receipts += 1
        counts[arm][report['class']] += 1
    require(paths == {str(p.relative_to(root)) for p in (root / 'receipts').glob('*/receipt.json')},
            'Unscored receipt')
    score = read_json(root / 'author-prediction-score.json')
    require(set(score['arms']) == set(predictions) and summary['author_prediction'] == score,
            'Prediction score population mismatch')
    matches = 0
    lines = []
    for arm in schedule:
        actual = dict(counts[arm])
        status = 'MATCH' if actual == predictions[arm]['class_counts'] else 'MISMATCH'
        recorded = score['arms'][arm]
        require(recorded['observed_class_counts'] == actual and recorded['status'] == status
                and recorded['prediction'] == predictions[arm]
                and recorded['planned'] == total and recorded['observed'] == total,
                'Prediction score differs from receipt counts')
        matches += status == 'MATCH'
        for cls, count in sorted(actual.items()):
            lines.append(f'[{arm}] [{anchors["model_identifier"]}] [{count}/{total}] [{cls}]')
    require(score['status'] == ('MATCH' if matches == len(schedule) else 'MISMATCH'),
            'Aggregate prediction score mismatch')
    finalization = verify_finalization(root, config, expected['receipt_count'])
    return {'status': 'PASS', 'run': run, 'installed_sdk_version': version('swiftapi-python'),
            'verified_receipts': len(paths), 'model_receipts_with_non_eos_identity': model_receipts,
            'prediction_matches': matches, 'prediction_arms': len(schedule),
            'ledger_status': finalization['status'], 'result_lines': lines,
            'full_model_forward_pass_reproduced': False,
            'numerical_gate_recomputation': 'SUPPLIED_FULL_VERIFIER_RECORDS_NOT_REEXECUTED'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', choices=('PRIMARY', 'SECONDARY'), required=True)
    parser.add_argument('--archive', type=Path, required=True)
    args = parser.parse_args()
    try:
        expected = read_json(ROOT / 'ARCHIVES.json')[args.run]
        anchors = read_json(ROOT / 'TRUST_ANCHORS.json')
        with tempfile.TemporaryDirectory(prefix='swiftapi-evidence-') as temporary:
            folder = Path(temporary)
            members = extract_archive(args.archive, folder, expected)
            report = verify_run(folder, args.run, expected, anchors)
            report['manifest_files'] = members
            print(json.dumps(report, indent=2))
    except Exception as exc:
        print(json.dumps({'status': 'FAIL', 'reason': str(exc)}))
        raise SystemExit(1) from None


if __name__ == '__main__':
    main()
