import json

import paths
from agent import build_agent, system_prompt
from langchain_core.messages import AIMessage, HumanMessage
from reset_workspace import reset_workspace
from skill_catalog import parse_frontmatter, scan_skills
from tests.conftest import ScriptedChatModel
from tools import read_file


def test_refund_catalog_progressive_loading_and_reset(lab_dirs):
    location = "skills/refund-policy/SKILL.md"
    text = (paths.WORKSPACE_DIR / location).read_text(encoding="utf-8")
    body = text.split("---", 2)[2].strip()
    template = "skills/refund-policy/references/answer-template.md"
    ref = (paths.WORKSPACE_DIR / template).read_text(encoding="utf-8")
    assert parse_frontmatter(text)["name"] == "refund-policy"
    assert [s.name for s in scan_skills(paths.WORKSPACE_DIR).skills] == ["refund-policy", "weekly-report"]
    prompt = system_prompt()
    assert location in prompt and body not in prompt and ref not in prompt
    assert "answer-template.md" not in prompt
    for forbidden in ("policy-before-oct", "policy-from-oct", "refund-alpha", "refund-beta", "2026-10-01"):
        assert forbidden not in text and forbidden not in prompt
    assert json.loads(read_file.invoke({"path": template}))["content"] == ref
    reset_workspace()
    assert (paths.WORKSPACE_DIR / location).read_text(encoding="utf-8") == text
    assert (paths.WORKSPACE_DIR / template).read_text(encoding="utf-8") == ref


def test_skill_and_reference_reach_model_only_after_read(lab_dirs):
    model = ScriptedChatModel(responses=[
        AIMessage(content="", tool_calls=[{"id": "s", "name": "read_file", "args": {"path": "skills/refund-policy/SKILL.md"}}]),
        AIMessage(content="", tool_calls=[{"id": "r", "name": "read_file", "args": {"path": "skills/refund-policy/references/answer-template.md"}}]),
        AIMessage(content="Offline plumbing test only."),
    ])
    build_agent(model).invoke({"messages": [HumanMessage(content="Tra cứu hoàn tiền.")]})
    assert len(model.received) == 3
    assert "Quy trình tra cứu hoàn tiền" not in str(model.received[0])
    assert "Quy trình tra cứu hoàn tiền" in str(model.received[1])
    assert "Kết quả tra cứu hoàn tiền" in str(model.received[2])
