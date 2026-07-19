# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, Field

from .classifier import AssetProfile, Sensitivity


class PolicyDecision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    ESCALATE = "ESCALATE"


class ReplicationConfig(BaseModel):
    factor: int = Field(ge=1, le=9)
    strategy: str
    geozones: list[str]


class EncryptionConfig(BaseModel):
    algorithm: str
    key_id: str
    rotation_cron: str


class AccessConfig(BaseModel):
    roles: list[str]
    timewindows: list[str] = []
    georestrictions: list[str] = []


class RetentionConfig(BaseModel):
    default_days: int = Field(ge=1)
    legal_hold_days: int = Field(default=0, ge=0)
    destruction_method: str = "crypto-erasure"


class StoragePolicy(BaseModel):
    ringname: str
    sensitivity: Literal["UNCLASSIFIED", "SENSITIVE", "CLASSIFIED", "TOP_SECRET"]
    replication: ReplicationConfig
    encryption: EncryptionConfig
    accesscontrol: AccessConfig
    retention: RetentionConfig


@dataclass(frozen=True)
class StorageOperation:
    operation: str
    asset_id: str
    actor: str
    actor_roles: list[str]
    asset_profile: AssetProfile
    region: str | None = None


@dataclass(frozen=True)
class DecisionResult:
    decision: PolicyDecision
    reason: str
    policy_name: str | None


class PolicyEngine:
    def __init__(self) -> None:
        self._policies: dict[str, StoragePolicy] = {}
        self._audit_log: list[dict[str, str]] = []

    def load_policies(self, config_dir: str | Path) -> None:
        for file in Path(config_dir).glob("*.yaml"):
            data = yaml.safe_load(file.read_text())
            policy = StoragePolicy.model_validate(data)
            self._policies[policy.ringname] = policy

    def get_policy(self, asset_profile: AssetProfile) -> StoragePolicy:
        if asset_profile.storage_ring not in self._policies:
            raise KeyError(f"No policy for ring {asset_profile.storage_ring}")
        return self._policies[asset_profile.storage_ring]

    def enforce(self, op: StorageOperation) -> DecisionResult:
        policy = self.get_policy(op.asset_profile)

        if op.asset_profile.sensitivity.value != policy.sensitivity:
            result = DecisionResult(
                decision=PolicyDecision.ESCALATE,
                reason="Asset sensitivity does not match target policy ring.",
                policy_name=policy.ringname,
            )
            self._audit(op, result)
            return result

        if not set(op.actor_roles).intersection(policy.accesscontrol.roles):
            result = DecisionResult(
                decision=PolicyDecision.DENY,
                reason="Actor lacks required role for storage ring.",
                policy_name=policy.ringname,
            )
            self._audit(op, result)
            return result

        if (
            op.asset_profile.sensitivity == Sensitivity.TOP_SECRET
            or op.asset_profile.sensitivity == Sensitivity.CLASSIFIED
        ) and op.operation in {"delete", "export", "rekey"}:
            result = DecisionResult(
                decision=PolicyDecision.ESCALATE,
                reason="High-sensitivity operation requires human gate.",
                policy_name=policy.ringname,
            )
            self._audit(op, result)
            return result

        if policy.accesscontrol.georestrictions and op.region:
            if op.region not in policy.accesscontrol.georestrictions:
                result = DecisionResult(
                    decision=PolicyDecision.DENY,
                    reason="Region is not permitted by policy.",
                    policy_name=policy.ringname,
                )
                self._audit(op, result)
                return result

        result = DecisionResult(
            decision=PolicyDecision.ALLOW,
            reason="Operation satisfies policy requirements.",
            policy_name=policy.ringname,
        )
        self._audit(op, result)
        return result

    def evaluate_retention(self, assets: list[dict]) -> list[str]:
        deletion_queue: list[str] = []
        for asset in assets:
            profile = asset["asset_profile"]
            policy = self.get_policy(profile)
            age_days = asset["age_days"]
            if age_days > (policy.retention.default_days + policy.retention.legal_hold_days):
                deletion_queue.append(asset["asset_id"])
        return deletion_queue

    def audit_log(self) -> list[dict[str, str]]:
        return list(self._audit_log)

    def _audit(self, op: StorageOperation, result: DecisionResult) -> None:
        self._audit_log.append(
            {
                "operation": op.operation,
                "asset_id": op.asset_id,
                "actor": op.actor,
                "decision": result.decision.value,
                "reason": result.reason,
                "policy": result.policy_name or "",
            }
        )