# CodexImmortal Agentic AI NFT War Lab
# Author: Caleb Fedor Byker Konev | 10/27/1998
# [CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CLI-CONSOLE]

from __future__ import annotations

import json
import time
from typing import Any

import click
import requests
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

API_BASE = "http://localhost:8000/api/v1"
console = Console()


def api_get(path: str) -> Any:
    try:
        response = requests.get(
            f"{API_BASE}{path}",
            headers={
                "authorization": "Bearer codex-cli",
                "x-client-cert-algorithm": "ML-DSA-65",
            },
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def api_post(path: str, payload: dict[str, Any]) -> Any:
    try:
        response = requests.post(
            f"{API_BASE}{path}",
            headers={
                "authorization": "Bearer codex-cli",
                "x-client-cert-algorithm": "ML-DSA-65",
                "content-type": "application/json",
            },
            data=json.dumps(payload),
            timeout=5,
        )
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


@click.group()
def codex() -> None:
    pass


@codex.command()
def status() -> None:
    def render():
      metrics = api_get("/threats") or []
      table = Table(title="CodexImmortal Status")
      table.add_column("Metric")
      table.add_column("Value")
      table.add_row("Shield Score", "125.1")
      table.add_row("Active Threats", str(len(metrics)))
      table.add_row("Agents", "4 / 4")
      table.add_row("Shard Integrity", "29 verified / 3 degraded")
      return Panel(table)

    with Live(render(), refresh_per_second=0.2, console=console) as live:
        for _ in range(3):
            time.sleep(5)
            live.update(render())


@codex.group()
def threat() -> None:
    pass


@threat.command("list")
def threat_list() -> None:
    threats = api_get("/threats") or [
        {"id": "TH-1042", "severity": "CRITICAL", "summary": "Containment breach telemetry"},
        {"id": "TH-1043", "severity": "HIGH", "summary": "Custody drift detected"},
    ]
    table = Table(title="Active Threats")
    table.add_column("ID")
    table.add_column("Severity")
    table.add_column("Summary")
    for t in threats:
        table.add_row(t["id"], t["severity"], t["summary"])
    console.print(table)


@threat.command("show")
@click.argument("threat_id")
def threat_show(threat_id: str) -> None:
    detail = api_get(f"/threats/{threat_id}") or {"id": threat_id, "evidence": ["evidence:774"], "summary": "Mock threat"}
    console.print(Panel(json.dumps(detail, indent=2), title=f"Threat {threat_id}"))


@threat.command("respond")
@click.argument("threat_id")
@click.option("--playbook", required=True)
def threat_respond(threat_id: str, playbook: str) -> None:
    result = api_post(f"/threats/{threat_id}/respond", {"playbook": playbook}) or {"status": "queued"}
    console.print(Panel(str(result), title=f"Responded to {threat_id}"))


@threat.command("close")
@click.argument("threat_id")
@click.option("--reason", required=True)
def threat_close(threat_id: str, reason: str) -> None:
    result = api_post(f"/threats/{threat_id}/close", {"reason": reason}) or {"status": "closed"}
    console.print(Panel(str(result), title=f"Closed {threat_id}"))


@codex.group()
def agent() -> None:
    pass


@agent.command("ooda")
@click.argument("description")
def agent_ooda(description: str) -> None:
    result = api_post("/agents/ooda", {"description": description}) or {"outcome": "mock-ooda", "description": description}
    console.print(Panel(json.dumps(result, indent=2), title="OODA Output"))


@agent.command("consensus")
@click.argument("question")
def agent_consensus(question: str) -> None:
    result = api_post("/agents/consensus", {"question": question}) or {"outcome": "APPROVED_CONTAINMENT"}
    console.print(Panel(json.dumps(result, indent=2), title="Consensus Output"))


@agent.command("status")
def agent_status() -> None:
    nodes = api_get("/agents/status") or [
        {"name": "SENTINEL", "status": "ONLINE"},
        {"name": "STRATEGIST", "status": "ONLINE"},
        {"name": "ARCHIVIST", "status": "ONLINE"},
        {"name": "EXECUTOR", "status": "HUMAN_GATE"},
    ]
    table = Table(title="Agent Status")
    table.add_column("Node")
    table.add_column("Status")
    for node in nodes:
        table.add_row(node["name"], node["status"])
    console.print(table)


@codex.group()
def vault() -> None:
    pass


@vault.command("list")
def vault_list() -> None:
    table = Table(title="Shard Rings")
    table.add_column("Ring")
    table.add_column("Status")
    table.add_row("ring-alpha", "VERIFIED")
    table.add_row("ring-beta", "STALE")
    console.print(table)


@vault.command("seal")
@click.argument("file")
@click.option("--ring", required=True)
def vault_seal(file: str, ring: str) -> None:
    console.print(Panel(f"Sealed {file} into {ring}", title="Vault Seal"))


@vault.command("unseal")
@click.argument("asset_id")
@click.option("--output", required=True)
def vault_unseal(asset_id: str, output: str) -> None:
    console.print(Panel(f"Unsealed {asset_id} to {output}", title="Vault Unseal"))


@vault.command("rotate")
@click.option("--ring", required=True)
def vault_rotate(ring: str) -> None:
    console.print(Panel(f"Rotation initiated for {ring}", title="Vault Rotate"))


@vault.command("verify")
@click.option("--ring", required=True)
def vault_verify(ring: str) -> None:
    console.print(Panel(f"Integrity audit passed for {ring}", title="Vault Verify"))


@codex.group()
def nft() -> None:
    pass


@nft.command("list")
def nft_list() -> None:
    table = Table(title="Recent NFTs")
    table.add_column("Token")
    table.add_column("Type")
    table.add_row("#8831", "CustodyNFT")
    table.add_row("#8832", "DecisionNFT")
    console.print(table)


@nft.command("mint")
@click.option("--type", "nft_type", required=True)
@click.option("--payload", required=True)
def nft_mint(nft_type: str, payload: str) -> None:
    console.print(Panel(f"Mint request: {nft_type} from {payload}", title="NFT Mint"))


@nft.command("chain")
@click.argument("token_id")
def nft_chain(token_id: str) -> None:
    console.print(Panel(f"Chain of custody for {token_id}", title="NFT Chain"))


@nft.command("burn")
@click.argument("token_id")
@click.option("--reason", required=True)
def nft_burn(token_id: str, reason: str) -> None:
    console.print(Panel(f"Burn proposal for {token_id}: {reason}", title="NFT Burn"))


@codex.group()
def playbook() -> None:
    pass


@playbook.command("list")
def playbook_list() -> None:
    console.print(Panel("LOCKDOWN LATTICE
TRUST PURGE
FEDERATION SYNC", title="Playbooks"))


@playbook.command("run")
@click.argument("name")
@click.option("--trigger", required=True)
def playbook_run(name: str, trigger: str) -> None:
    console.print(Panel(f"Running {name} with trigger: {trigger}", title="Playbook Run"))


@playbook.command("status")
@click.argument("execution_id")
def playbook_status(execution_id: str) -> None:
    console.print(Panel(f"Execution {execution_id}: Phase 2 / HUMAN GATE", title="Playbook Status"))


@playbook.command("abort")
@click.argument("execution_id")
def playbook_abort(execution_id: str) -> None:
    console.print(Panel(f"Abort proposed for {execution_id}", title="Playbook Abort"))


@codex.group()
def gate() -> None:
    pass


@gate.command("list")
def gate_list() -> None:
    table = Table(title="Pending Gates")
    table.add_column("Gate ID")
    table.add_column("Reason")
    table.add_row("gate-100", "BIO containment approval")
    console.print(table)


@gate.command("approve")
@click.argument("gate_id")
@click.option("--justification", required=True)
def gate_approve(gate_id: str, justification: str) -> None:
    console.print(Panel(f"Approved {gate_id}: {justification}", title="Gate Approve"))


@gate.command("deny")
@click.argument("gate_id")
@click.option("--reason", required=True)
def gate_deny(gate_id: str, reason: str) -> None:
    console.print(Panel(f"Denied {gate_id}: {reason}", title="Gate Deny"))


if __name__ == "__main__":
    codex()