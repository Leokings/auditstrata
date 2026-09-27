import hashlib
import json


SECRET_A = "a" * 64
SECRET_B = "b" * 64
STRATA = ["Routine", "Exceptional"]
RECORDS = [
    ("R0", "Routine monthly inventory entry."),
    ("R1", "Exceptional manual override entry."),
    ("R2", "Routine scheduled reconciliation entry."),
    ("R3", "Exceptional after-hours adjustment entry."),
]


def _commitment(secret: str) -> str:
    return hashlib.sha256(f"auditstrata/v2|seed|{secret}".encode()).hexdigest()


def _address(value) -> str:
    if isinstance(value, (bytes, bytearray)):
        return "0x" + bytes(value).hex()
    return str(value)


def _open(contract, vm, owner, auditor, key="q3", size=2):
    vm.sender = owner
    return contract.open_population(key, json.dumps(STRATA), size, _address(auditor))


def _prepare(contract, vm, owner, auditor, secret=SECRET_A, key="q3", size=2, seal=True):
    population_id = _open(contract, vm, owner, auditor, key, size)
    vm.sender = auditor
    contract.commit_seed(population_id, _commitment(secret))
    vm.sender = owner
    for record_key, description in RECORDS:
        contract.append_record(population_id, record_key, description)
    if seal:
        contract.seal_population(population_id)
    return population_id


def _draw(contract, vm, population_id, auditor, secret=SECRET_A, labels=None):
    vm.sender = auditor
    vm.mock_llm(
        r".*Assign every public record to exactly one closed audit stratum.*",
        json.dumps({"strata": labels or [0, 1, 0, 1]}),
    )
    contract.draw_sample(population_id, secret)


def test_commit_seal_reveal_draw_is_stratified(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    _draw(contract, direct_vm, population_id, direct_bob)
    state = contract.get_population(population_id)
    assert state["schema"] == "auditstrata/population/v2"
    assert state["state"] == "DRAWN"
    assert state["records_digest"]
    assert state["sampling_seed_digest"]
    sampled_strata = {contract.sampled_record(population_id, slot)["stratum_index"] for slot in range(2)}
    assert sampled_strata == {0, 1}


def test_owner_cannot_name_itself_as_auditor(contract, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("auditor_must_be_distinct"):
        contract.open_population("self-audit", json.dumps(STRATA), 1, _address(direct_alice))


def test_zero_address_cannot_be_auditor(contract, direct_vm, direct_alice):
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("auditor_must_be_distinct"):
        contract.open_population("zero-auditor", json.dumps(STRATA), 1, "0x" + "0" * 40)


def test_strata_names_are_unique_case_insensitively(contract, direct_vm, direct_alice, direct_bob):
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("duplicate_stratum"):
        contract.open_population("duplicate-strata", json.dumps(["Routine", " routine "]), 1, _address(direct_bob))


def test_records_cannot_be_added_before_auditor_commitment(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("collection_closed"):
        contract.append_record(population_id, "R0", RECORDS[0][1])


def test_only_auditor_can_commit_seed(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_auditor"):
        contract.commit_seed(population_id, _commitment(SECRET_A))


def test_seed_commitment_cannot_be_reused(contract, direct_vm, direct_alice, direct_bob):
    first = _open(contract, direct_vm, direct_alice, direct_bob, "first", 1)
    direct_vm.sender = direct_bob
    contract.commit_seed(first, _commitment(SECRET_A))
    second = _open(contract, direct_vm, direct_alice, direct_bob, "second", 1)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("seed_commitment_used"):
        contract.commit_seed(second, _commitment(SECRET_A))


def test_population_cannot_be_sealed_without_enough_records(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob, size=2)
    direct_vm.sender = direct_bob
    contract.commit_seed(population_id, _commitment(SECRET_A))
    direct_vm.sender = direct_alice
    contract.append_record(population_id, "ONLY", "Only one record is available for sampling.")
    with direct_vm.expect_revert("insufficient_records"):
        contract.seal_population(population_id)


def test_population_is_immutable_after_seal(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("collection_closed"):
        contract.append_record(population_id, "LATE", "This record arrived after the immutable seal.")


def test_only_owner_can_append_or_seal(contract, direct_vm, direct_alice, direct_bob, direct_charlie):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob, "owner-writes", 1)
    direct_vm.sender = direct_bob
    contract.commit_seed(population_id, _commitment(SECRET_A))
    direct_vm.sender = direct_charlie
    with direct_vm.expect_revert("only_owner"):
        contract.append_record(population_id, "R0", RECORDS[0][1])
    with direct_vm.expect_revert("only_owner"):
        contract.seal_population(population_id)


def test_only_auditor_can_reveal_and_commitment_must_match(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("only_auditor"):
        contract.draw_sample(population_id, SECRET_A)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("seed_commitment_mismatch"):
        contract.draw_sample(population_id, SECRET_B)


def test_seed_material_must_be_exactly_32_bytes_of_hex(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob, "seed-format", 1)
    direct_vm.sender = direct_bob
    with direct_vm.expect_revert("invalid_seed_commitment"):
        contract.commit_seed(population_id, "not-a-digest")


def test_seed_derived_stratum_order_removes_fixed_index_bias(contract, direct_vm, direct_alice, direct_bob):
    population_id = _open(contract, direct_vm, direct_alice, direct_bob, "single", 1)
    direct_vm.sender = direct_bob
    contract.commit_seed(population_id, _commitment(SECRET_B))
    direct_vm.sender = direct_alice
    two_records = RECORDS[:2]
    for record_key, description in two_records:
        contract.append_record(population_id, record_key, description)
    contract.seal_population(population_id)

    canonical = json.dumps(
        [{"key": key, "description": description} for key, description in two_records],
        sort_keys=True,
        separators=(",", ":"),
    )
    records_digest = hashlib.sha256(f"auditstrata/v2|records|{canonical}".encode()).hexdigest()
    sampling_seed = hashlib.sha256(
        f"auditstrata/v2|draw|{population_id}|{records_digest}|{SECRET_B}".encode()
    ).hexdigest()
    expected_first_stratum = min(
        range(2),
        key=lambda index: (hashlib.sha256(f"{sampling_seed}|STRATUM|{index}".encode()).hexdigest(), index),
    )

    _draw(contract, direct_vm, population_id, direct_bob, SECRET_B, [0, 1])
    assert contract.sampled_record(population_id, 0)["stratum_index"] == expected_first_stratum


def test_revealed_secret_is_not_stored(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    _draw(contract, direct_vm, population_id, direct_bob)
    state = contract.get_population(population_id)
    assert state["seed_commitment"] == _commitment(SECRET_A)
    assert SECRET_A not in json.dumps(state, sort_keys=True)


def test_only_auditor_acknowledges(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    _draw(contract, direct_vm, population_id, direct_bob)
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("only_auditor"):
        contract.acknowledge_sample(population_id, 0, "Owner cannot impersonate the named auditor.")


def test_acknowledged_sample_closes(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    _draw(contract, direct_vm, population_id, direct_bob)
    direct_vm.sender = direct_bob
    contract.acknowledge_sample(population_id, 0, "Audited selected record and stored the public outcome reference.")
    contract.acknowledge_sample(population_id, 1, "Audited selected record and stored the public outcome reference.")
    direct_vm.sender = direct_alice
    contract.close_population(population_id)
    assert contract.sample_is_closed(population_id) is True


def test_owner_cannot_close_before_every_sample_is_acknowledged(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    _draw(contract, direct_vm, population_id, direct_bob)
    direct_vm.sender = direct_bob
    contract.acknowledge_sample(population_id, 0, "Auditor completed the first selected record review.")
    direct_vm.sender = direct_alice
    with direct_vm.expect_revert("sample_not_acknowledged"):
        contract.close_population(population_id)


def test_sample_slot_can_only_be_acknowledged_once(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    _draw(contract, direct_vm, population_id, direct_bob)
    direct_vm.sender = direct_bob
    contract.acknowledge_sample(population_id, 0, "Auditor completed the selected record review.")
    with direct_vm.expect_revert("invalid_sample_slot"):
        contract.acknowledge_sample(population_id, 0, "A duplicate acknowledgement must be rejected.")


def test_model_must_label_every_record(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    direct_vm.mock_llm(r".*Assign every public record.*", json.dumps({"strata": [0, 1]}))
    with direct_vm.expect_revert("[LLM_ERROR] invalid_strata_vector"):
        contract.draw_sample(population_id, SECRET_A)


def test_model_cannot_return_out_of_range_or_boolean_strata(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob, key="out-of-range")
    direct_vm.sender = direct_bob
    direct_vm.mock_llm(r".*Assign every public record.*", json.dumps({"strata": [0, 1, 0, 2]}))
    with direct_vm.expect_revert("[LLM_ERROR] invalid_strata_vector"):
        contract.draw_sample(population_id, SECRET_A)


def test_model_cannot_return_boolean_strata(contract, direct_vm, direct_alice, direct_bob):
    population_id = _prepare(contract, direct_vm, direct_alice, direct_bob, key="boolean")
    direct_vm.sender = direct_bob
    direct_vm.mock_llm(r".*Assign every public record.*", json.dumps({"strata": [0, 1, 0, True]}))
    with direct_vm.expect_revert("[LLM_ERROR] invalid_strata_vector"):
        contract.draw_sample(population_id, SECRET_A)
