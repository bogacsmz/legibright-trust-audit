"""set_auditor_owner attaches Legibright as an *Auditor* (custom type), never a data owner."""
from datahub.metadata import schema_classes as S

from trust_layer import writeback as wb


class _FakeGraph:
    def __init__(self):
        self.emitted = []

    def exists(self, urn):
        return False

    def get_aspect(self, urn, cls):
        return None

    def emit_mcp(self, mcp):
        self.emitted.append(mcp)


def test_auditor_owner_uses_custom_auditor_type_not_data_owner():
    g = _FakeGraph()
    wb.set_auditor_owner(g, "urn:li:dataset:(urn:li:dataPlatform:sqlite,x,PROD)")

    # the ownership-type entity is defined as "Auditor"
    type_infos = [m.aspect for m in g.emitted if isinstance(m.aspect, S.OwnershipTypeInfoClass)]
    assert type_infos and type_infos[0].name == "Auditor"

    # the dataset gets an owner with the CUSTOM Auditor type — NOT DATAOWNER
    owns = [m.aspect for m in g.emitted if isinstance(m.aspect, S.OwnershipClass)]
    assert owns, "no Ownership aspect emitted"
    owner = owns[-1].owners[0]
    assert owner.owner == "urn:li:corpuser:trust-layer-agent"
    assert owner.typeUrn == wb._OWNERSHIP_TYPE_URN
    assert owner.type == S.OwnershipTypeClass.CUSTOM
    assert owner.type != S.OwnershipTypeClass.DATAOWNER
