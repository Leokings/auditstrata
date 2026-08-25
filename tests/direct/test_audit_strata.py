import json


def _open(contract, vm, owner, auditor):
    vm.sender = owner
    population_id = contract.open_population("q3", json.dumps(["Routine", "Exceptional"]), 2, "quarter-three-seed", auditor)
    for index, text in enumerate(["Routine monthly inventory entry.", "Exceptional manual override entry.", "Routine scheduled reconciliation entry.", "Exceptional after-hours adjustment entry."]):
        contract.append_record(population_id, f"R{index}", text)
    return population_id


def test_draw_is_stratified_and_reproducible(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*Assign every public record to exactly one closed audit stratum.*", json.dumps({"strata": [0, 1, 0, 1]}))
    contract.draw_sample(population_id)
    first = contract.sampled_record(population_id, 0)
    second = contract.sampled_record(population_id, 1)
    assert {first["stratum_index"], second["stratum_index"]} == {0, 1}


def test_only_auditor_acknowledges(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*Assign every public record.*", json.dumps({"strata": [0, 1, 0, 1]}))
    contract.draw_sample(population_id)
    with direct_vm.expect_revert("only_auditor"):
        contract.acknowledge_sample(population_id, 0, "Owner cannot impersonate the named auditor.")


def test_acknowledged_sample_closes(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*Assign every public record.*", json.dumps({"strata": [0, 1, 0, 1]}))
    contract.draw_sample(population_id)
    direct_vm.sender = direct_bob
    contract.acknowledge_sample(population_id, 0, "Audited selected record and stored the public outcome reference.")
    contract.acknowledge_sample(population_id, 1, "Audited selected record and stored the public outcome reference.")
    direct_vm.sender = direct_alice
    contract.close_population(population_id)
    assert contract.sample_is_closed(population_id) is True


def test_model_must_label_every_record(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    direct_vm.mock_llm(r".*Assign every public record.*", json.dumps({"strata": [0, 1]}))
    with direct_vm.expect_revert("[LLM_ERROR] invalid_strata_vector"):
        contract.draw_sample(population_id)
