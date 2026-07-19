# CODEXIMMORTAL AGENTIC AI NFT WAR LAB
# CODEX-TAG: CALEB-FEDOR-BYKER-KONEV-10271998-CODEXIMMORTAL

from __future__ import annotations
import json
import shutil
from hashlib import sha3_256
from pathlib import Path

import click


def _manifest_path(vault_path: Path) -> Path:
    return vault_path.with_suffix(vault_path.suffix + ".manifest.json")


@click.group()
def cli() -> None:
    """Air-gapped dead-drop vault operations."""
    pass


@cli.command("seal")
@click.option("--input", "input_path", required=True, type=click.Path(exists=True))
@click.option("--output", "output_path", required=True, type=click.Path())
@click.option("--sensitivity", default="SENSITIVE")
def seal(input_path: str, output_path: str, sensitivity: str) -> None:
    src = Path(input_path)
    dst = Path(output_path)

    payload = src.read_bytes()
    digest = sha3_256(payload).hexdigest()
    dst.write_bytes(payload)

    manifest = {
        "vault_id": digest,
        "source_name": src.name,
        "size_bytes": len(payload),
        "sensitivity": sensitivity,
        "status": "SEALED",
    }
    _manifest_path(dst).write_text(json.dumps(manifest, indent=2))
    click.echo(f"Sealed vault created: {dst}")


@cli.command("open")
@click.option("--vault", "vault_path", required=True, type=click.Path(exists=True))
@click.option("--output", "output_dir", required=True, type=click.Path())
def open_vault(vault_path: str, output_dir: str) -> None:
    vault = Path(vault_path)
    manifest = json.loads(_manifest_path(vault).read_text())
    payload = vault.read_bytes()

    if sha3_256(payload).hexdigest() != manifest["vault_id"]:
        raise click.ClickException("Vault integrity check failed.")

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / manifest["source_name"]
    out_file.write_bytes(payload)
    click.echo(f"Opened vault to: {out_file}")


@cli.command("verify")
@click.option("--vault", "vault_path", required=True, type=click.Path(exists=True))
def verify(vault_path: str) -> None:
    vault = Path(vault_path)
    manifest = json.loads(_manifest_path(vault).read_text())
    payload = vault.read_bytes()

    status = "VERIFIED" if sha3_256(payload).hexdigest() == manifest["vault_id"] else "TAMPERED"
    click.echo(status)


@cli.command("inventory")
@click.option("--vault-dir", "vault_dir", required=True, type=click.Path(exists=True))
def inventory(vault_dir: str) -> None:
    root = Path(vault_dir)
    for manifest_file in root.glob("*.manifest.json"):
        manifest = json.loads(manifest_file.read_text())
        click.echo(
            f"{manifest['vault_id']} | {manifest['source_name']} | "
            f"{manifest['sensitivity']} | {manifest['status']}"
        )


@cli.command("transfer")
@click.option("--vault", "vault_path", required=True, type=click.Path(exists=True))
@click.option("--destination", required=True, type=click.Path())
def transfer(vault_path: str, destination: str) -> None:
    vault = Path(vault_path)
    manifest = _manifest_path(vault)
    dest = Path(destination)
    dest.mkdir(parents=True, exist_ok=True)

    shutil.copy2(vault, dest / vault.name)
    shutil.copy2(manifest, dest / manifest.name)
    click.echo(f"Transferred {vault.name} and manifest to {dest}")


if __name__ == "__main__":
    cli()