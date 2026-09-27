import hashlib
import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.contracts.contract import Contract
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt), json.dumps(receipt, default=str)


def _contract(address, account):
    # glsim 0.1's schema extractor does not yet recognize the pinned GenLayer
    # SDK class wrapper. The live StudioNet test uses the network schema; this
    # local integration fixture declares only the write/view distinction that
    # gltest needs to encode calls.
    methods = {
        "open_population": False,
        "commit_seed": False,
        "append_record": False,
        "seal_population": False,
        "draw_sample": False,
        "acknowledge_sample": False,
        "close_population": False,
        "get_population": True,
        "sampled_record": True,
        "sample_is_closed": True,
    }
    schema = {
        "ctor": {"params": [], "kwparams": {}},
        "methods": {
            name: {"params": [], "kwparams": {}, "ret": "any", "readonly": readonly}
            for name, readonly in methods.items()
        },
    }
    return Contract.new(address=address, schema=schema, account=account)


def test_five_validator_stratified_draw():
    owner, auditor = create_accounts(2)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "audit_strata.py")
    receipt = factory.deploy_contract_tx(args=[], account=owner, wait_transaction_status=TransactionStatus.FINALIZED)
    _ok(receipt)
    address = extract_contract_address(receipt)
    contract = _contract(address, owner)
    auditor_contract = _contract(address, auditor)
    population_id = f"{str(owner.address).lower()}:Q3"
    secret = "a" * 64
    commitment = hashlib.sha256(f"auditstrata/v2|seed|{secret}".encode()).hexdigest()
    _ok(contract.open_population(args=["q3", json.dumps(["Routine", "Exceptional"]), 2, auditor.address]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(auditor_contract.commit_seed(args=[population_id, commitment]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    for index, description in enumerate(["Routine monthly inventory entry.", "Exceptional manual override entry.", "Routine scheduled reconciliation entry.", "Exceptional after-hours adjustment entry."]):
        _ok(contract.append_record(args=[population_id, f"R{index}", description]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(contract.seal_population(args=[population_id]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {"Assign every public record to exactly one closed audit stratum": json.dumps({"strata": [0, 1, 0, 1]})}})
    context = {"validators": [v.to_dict() for v in validators], "genvm_datetime": "2026-08-25T12:00:00Z"}
    _ok(auditor_contract.draw_sample(args=[population_id, secret]).transact(transaction_context=context, wait_transaction_status=TransactionStatus.FINALIZED))
    state = contract.get_population(args=[population_id]).call()
    assert state["schema"] == "auditstrata/population/v2"
    assert state["state"] == "DRAWN"
    assert len(state["sample"]) == 2
    _ok(auditor_contract.acknowledge_sample(args=[population_id, 0, "Auditor completed the first selected record review."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(auditor_contract.acknowledge_sample(args=[population_id, 1, "Auditor completed the second selected record review."]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    _ok(contract.close_population(args=[population_id]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    assert contract.sample_is_closed(args=[population_id]).call() is True
