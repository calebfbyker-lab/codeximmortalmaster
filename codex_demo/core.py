"""Synthetic role simulation; no runtime imports or external actions."""
import hashlib
import json
import math

DOMAINS = {'CYBER', 'KINETIC', 'BIO', 'SPACE', 'OT', 'ICS', 'OT/ICS'}
CLASSIFICATIONS = {'UNCLASSIFIED', 'SENSITIVE', 'CONFIDENTIAL', 'SECRET', 'TOP_SECRET', 'TS_SCI'}
OPERATIONS = {'recommend', 'master_shard', 'registry_change', 'doctrine_change', 'funding', 'multi_theater_scaleup'}
FIELDS = {'id', 'synthetic', 'domain', 'classification', 'operation', 'shield_impact', 'anomaly_score'}

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()

def envelope(event):
    return {'event': event, 'sha256': digest(event)}

def scenario(name):
    event = dict(id='synthetic-' + name, synthetic=True, domain='CYBER', classification='UNCLASSIFIED', operation='recommend', shield_impact=2.0, anomaly_score=0.25)
    if name == 'human_gate':
        event.update(shield_impact=9.0, anomaly_score=0.9)
    elif name not in {'routine', 'tampered'}:
        raise ValueError('Unknown scenario')
    value = envelope(event)
    if name == 'tampered':
        value['event']['anomaly_score'] = 0.99
    return value

def validate(value):
    if not isinstance(value, dict) or set(value) != {'event', 'sha256'}:
        raise ValueError('Invalid envelope fields')
    event = value['event']
    if not isinstance(event, dict) or set(event) != FIELDS:
        raise ValueError('Invalid event fields')
    if event['synthetic'] is not True:
        raise ValueError('Only synthetic events accepted')
    if not isinstance(event['id'], str) or not 1 <= len(event['id']) <= 128:
        raise ValueError('Invalid event id')
    for field, allowed in [('domain', DOMAINS), ('classification', CLASSIFICATIONS), ('operation', OPERATIONS)]:
        if not isinstance(event[field], str) or event[field] not in allowed:
            raise ValueError('Unknown ' + field)
    for field, upper in [('shield_impact', 10), ('anomaly_score', 1)]:
        score = event[field]
        if type(score) not in (int, float) or not math.isfinite(score) or not 0 <= score <= upper:
            raise ValueError('Invalid ' + field)
    if value['sha256'] != digest(event):
        raise ValueError('Event hash mismatch')
    return event

def run(value):
    event = validate(value)
    reasons = []
    if event['domain'] != 'CYBER':
        reasons.append('gated_domain')
    if event['classification'] in {'TOP_SECRET', 'TS_SCI'}:
        reasons.append('gated_classification')
    if event['operation'] != 'recommend':
        reasons.append('gated_operation')
    if event['shield_impact'] > 8.5:
        reasons.append('shield_impact_above_8_5')
    decision = 'HUMAN_GATE' if reasons else 'SIMULATED'
    receipt = {
        'schema_version': 1, 'mode': 'OFFLINE_SIMULATION', 'event_id': event['id'],
        'event_sha256': value['sha256'], 'decision': decision, 'executed': False,
        'trace': [
            {'role': 'SENTINEL', 'anomaly_score': event['anomaly_score']},
            {'role': 'STRATEGIST', 'recommendation': 'review_synthetic_alert' if event['anomaly_score'] >= 0.7 else 'record_and_monitor'},
            {'role': 'POLICY', 'decision': decision, 'reasons': reasons},
            {'role': 'EXECUTOR', 'executed': False, 'simulation_completed': not reasons},
            {'role': 'ARCHIVIST', 'action': 'assemble_receipt'}],
        'limitations': ['Role simulation, not existing runtime', 'SHA-256 is not authentication', 'No PQC, BFT, NFT, LLM, or live execution']}
    return {'receipt': receipt, 'receipt_sha256': digest(receipt)}

def verify_receipt(value):
    return (isinstance(value, dict) and set(value) == {'receipt', 'receipt_sha256'}
            and isinstance(value['receipt'], dict) and digest(value['receipt']) == value['receipt_sha256'])
