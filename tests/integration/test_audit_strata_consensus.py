import json
from pathlib import Path
from gltest import get_contract_factory, get_validator_factory
from gltest.accounts import create_accounts
from gltest.assertions import tx_execution_succeeded
from gltest.types import TransactionStatus
from gltest.utils import extract_contract_address


def _ok(receipt):
    assert tx_execution_succeeded(receipt), json.dumps(receipt, default=str)


def test_five_validator_stratified_draw():
    owner, auditor = create_accounts(2)
    factory = get_contract_factory(contract_file_path=Path(__file__).resolve().parents[2] / "contracts" / "audit_strata.py")
    receipt = factory.deploy_contract_tx(args=[], account=owner, wait_transaction_status=TransactionStatus.FINALIZED)
    _ok(receipt)
    contract = factory.build_contract(extract_contract_address(receipt), account=owner)
    population_id = f"{str(owner.address).lower()}:Q3"
    _ok(contract.open_population(args=["q3", json.dumps(["Routine", "Exceptional"]), 2, "quarter-three-seed", auditor.address]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    for index, description in enumerate(["Routine monthly inventory entry.", "Exceptional manual override entry.", "Routine scheduled reconciliation entry.", "Exceptional after-hours adjustment entry."]):
        _ok(contract.append_record(args=[population_id, f"R{index}", description]).transact(wait_transaction_status=TransactionStatus.FINALIZED))
    validators = get_validator_factory().batch_create_mock_validators(5, mock_llm_response={"nondet_exec_prompt": {"Assign every public record to exactly one closed audit stratum": json.dumps({"strata": [0, 1, 0, 1]})}})
    context = {"validators": [v.to_dict() for v in validators], "genvm_datetime": "2026-08-25T12:00:00Z"}
    _ok(contract.draw_sample(args=[population_id]).transact(transaction_context=context, wait_transaction_status=TransactionStatus.FINALIZED))
    assert contract.get_population(args=[population_id]).call()["state"] == "DRAWN"
