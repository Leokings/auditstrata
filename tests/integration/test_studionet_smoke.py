import hashlib
import json
import os
from pathlib import Path
import secrets

import pytest
from gltest import get_contract_factory
from gltest.types import TransactionHashVariant, TransactionStatus
from gltest.utils import extract_contract_address

from tests.studionet_support import emit_record, ok, source_schema_proof, wallet_accounts


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(os.environ.get("RUN_STUDIONET") != "1", reason="opt-in live StudioNet test"),
]


def test_studionet_stratified_audit_draw():
    accounts = wallet_accounts("auditstrata", 2)
    owner, auditor = accounts[:2]
    source = Path(__file__).resolve().parents[2] / "contracts" / "audit_strata.py"
    factory = get_contract_factory(contract_file_path=source)
    deployed = ok(factory.deploy_contract_tx(args=[], account=owner, wait_transaction_status=TransactionStatus.FINALIZED))
    address = extract_contract_address(deployed)
    contract = factory.build_contract(address, account=owner)
    auditor_contract = factory.build_contract(address, account=auditor)
    population_id = f"{str(owner.address).lower()}:Q3"
    secret = secrets.token_hex(32)
    commitment = hashlib.sha256(f"auditstrata/v2|seed|{secret}".encode()).hexdigest()
    setup = [ok(contract.open_population(args=["q3", json.dumps(["Routine", "Exceptional"]), 2, auditor.address]).transact(wait_transaction_status=TransactionStatus.FINALIZED))]
    setup.append(ok(auditor_contract.commit_seed(args=[population_id, commitment]).transact(wait_transaction_status=TransactionStatus.FINALIZED)))
    for index, description in enumerate(["Routine monthly inventory entry.", "Exceptional manual override entry.", "Routine scheduled reconciliation entry.", "Exceptional after-hours adjustment entry."]):
        setup.append(ok(contract.append_record(args=[population_id, f"R{index}", description]).transact(wait_transaction_status=TransactionStatus.FINALIZED)))
    setup.append(ok(contract.seal_population(args=[population_id]).transact(wait_transaction_status=TransactionStatus.FINALIZED)))
    intelligent = ok(auditor_contract.draw_sample(args=[population_id, secret]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    state = contract.get_population(args=[population_id]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["schema"] == "auditstrata/population/v2" and state["state"] == "DRAWN" and len(state["sample"]) == 2
    for slot in range(len(state["sample"])):
        setup.append(ok(auditor_contract.acknowledge_sample(args=[population_id, slot, "Auditor completed the selected public record review."]).transact(wait_transaction_status=TransactionStatus.FINALIZED)))
    setup.append(ok(contract.close_population(args=[population_id]).transact(wait_transaction_status=TransactionStatus.FINALIZED)))
    state = contract.get_population(args=[population_id]).call(transaction_hash_variant=TransactionHashVariant.LATEST_FINAL)
    assert state["state"] == "CLOSED"
    proof = source_schema_proof(address, source, {"open_population", "commit_seed", "seal_population", "draw_sample", "acknowledge_sample", "close_population", "sampled_record"})
    emit_record("auditstrata", "A", address, deployed, setup, intelligent, accounts, proof, {"state": state["state"], "sample_indexes": state["sample"], "strata": state["labels"], "records_digest": state["records_digest"], "sampling_seed_digest": state["sampling_seed_digest"]})
