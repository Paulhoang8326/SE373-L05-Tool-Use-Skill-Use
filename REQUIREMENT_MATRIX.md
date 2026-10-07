# D05 Requirement Matrix

Đối chiếu toàn bộ HTML ngày 2026-10-07, không dùng report thay evidence.
Nguồn chính thức: [Block 1](https://pub.nndkhoa9.win/agentic-ai-engineering/d05-tool-use-skill-use/exercise-block-1.html), [Block 2](https://pub.nndkhoa9.win/agentic-ai-engineering/d05-tool-use-skill-use/exercise-block-2.html).
Paths dưới đây tính từ submission-d05. Các mục được nhóm theo contract, không đếm bullet HTML như các requirement độc lập.
Sequence/action/result/prompt/answer của từng trace: [TRACE_VERIFICATION.md](verification/TRACE_VERIFICATION.md).

## Block 1

| Requirement của đề | Block | File/Bằng chứng hiện có | Trạng thái |
|---|---|---|---|
| B1-01 Bản sao, giữ source gốc | Block 1 | original-hashes.json; verification/final-checks.json | PASS |
| B1-02 Hai policy đúng nội dung | Block 1 | block-1/stage-01-files và stage-02-skills/workspace/data/policies/refund-alpha.md, refund-beta.md; rename-proof | PASS |
| B1-03 Baseline Stage 00 | Block 1 | block-1/live-results/stage-00-baseline.json; mapped JSONL | PASS |
| B1-04 Source list_files Stage 01 | Block 1 | block-1/stage-01-files/tools/files.py | PASS |
| B1-05 Registration Stage 01 | Block 1 | block-1/stage-01-files/tools/__init__.py, agent.py | PASS |
| B1-06 Source list_files Stage 02 | Block 1 | block-1/stage-02-skills/tools/files.py | PASS |
| B1-07 Registration Stage 02 | Block 1 | block-1/stage-02-skills/tools/__init__.py, agent.py | PASS |
| B1-08 Direct-only listing | Block 1 | tests/test_list_files.py trong hai stage; full pytest logs | PASS |
| B1-09 Name, relative path, type | Block 1 | verification/*-direct-tools.json; test_list_files.py | PASS |
| B1-10 Deterministic sorting | Block 1 | test_list_files.py; direct JSON | PASS |
| B1-11 Reuse path/error convention | Block 1 | tools/files.py: _resolve, _error, _list | PASS |
| B1-12 Workspace boundary/symlink | Block 1 | test_list_files.py trên POSIX; full pytest | PASS |
| B1-13 File/missing path errors | Block 1 | direct JSON: NOT_A_DIRECTORY, DIRECTORY_NOT_FOUND | PASS |
| B1-14 Schema thực gửi model | Block 1 | actual model_request snapshots; test_agent.py | PASS |
| B1-15 Skill frontmatter/catalog | Block 1 | block-1/stage-02-skills/workspace/skills/refund-policy/SKILL.md; test_refund_policy.py | PASS |
| B1-16 Discovery, purchase-date selection | Block 1 | refund-policy/SKILL.md; A/B list/read JSONL | PASS |
| B1-17 Thiếu ngày/activation hỏi trước | Block 1 | SKILL.md kiểm tra cả ba trường; missing-activation trace | PASS |
| B1-18 Reference fields, không Bash | Block 1 | refund-policy/references/answer-template.md; stage tools; trace | PASS |
| B1-19 Case A đúng | Block 1 | block-1/traces/20261007-212439_ef587fcc_turn01_789e42d7.jsonl | PASS |
| B1-20 Case B đúng | Block 1 | block-1/traces/20261007-212604_df36474c_turn01_379cee7a.jsonl | PASS |
| B1-21 Rename, history mới | Block 1 | before/after live-results; policy-rename-proof.json; fresh conversation IDs | PASS |
| B1-22 Missing-information live | Block 1 | block-1/traces/20261007-210927_e9c6f44e_turn01_85f0232d.jsonl | PASS |
| B1-23 Direct dummy tests/pytest | Block 1 | verification/stage-01-files-direct-tools.json, stage-02-skills-direct-tools.json; 47/56 passed | PASS |
| B1-24 Required traces, analysis, câu hỏi cuối | Block 1 | block-1/analysis.md; traces trên; verification/TRACE_VERIFICATION.md | PASS |

## Block 2

| Requirement của đề | Block | File/Bằng chứng hiện có | Trạng thái |
|---|---|---|---|
| B2-01 Bản sao, không đổi agent/tools | Block 2 | original-hashes.json; final-checks.json byte/hash comparisons | PASS |
| B2-02 workload.csv Stage 03/04 | Block 2 | block-2/stage-03-bash và stage-04-script-skill/workspace/data/workload.csv | PASS |
| B2-03 Baseline Bash, duplicate logic | Block 2 | stage-03-baseline.json/JSONL; analysis.md code excerpt/event locations | PASS |
| B2-04 Mở rộng script hiện có | Block 2 | block-2/stage-04-script-skill/workspace/skills/csv-quality/scripts/check_csv.py | PASS |
| B2-05 Required finite nonnegative CLI | Block 2 | test_workload.py CLI cases; stderr/nonzero assertions | PASS |
| B2-06 Quality fields cũ giữ nguyên | Block 2 | existing tests; results/max-hours-8.json | PASS |
| B2-07 Trim, owner case-sensitive | Block 2 | test_workload.py whitespace/case assertions | PASS |
| B2-08 First occurrence reserves ID | Block 2 | test_first_invalid_occurrence_reserves_id_and_zero_is_valid | PASS |
| B2-09 Valid rows only, zero hợp lệ | Block 2 | workload/edge JSON; automated tests | PASS |
| B2-10 Exclusions đủ reasons | Block 2 | multiple-reasons tests; excluded_rows JSON | PASS |
| B2-11 Overload >, equality không overload | Block 2 | max-hours-8.json / max-hours-9.json; tests | PASS |
| B2-12 JSON fields/types/order/null ID | Block 2 | script; tests; direct outputs | PASS |
| B2-13 Success exit=0 dù lỗi dữ liệu | Block 2 | *-execution.json; Bash events threshold 8/9 | PASS |
| B2-14 Missing/unreadable/header errors | Block 2 | existing tests; missing-file-execution.json; missing-file-script trace | PASS |
| B2-15 Input immutable | Block 2 | before/after hashes; workspace/fixtures comparisons | PASS |
| B2-16 Skill hỏi/truyền ngưỡng hiện tại | Block 2 | csv-quality/SKILL.md; threshold and missing-threshold JSONL | PASS |
| B2-17 Reference contract cập nhật | Block 2 | csv-quality/references/report-template.md; agent reports | PASS |
| B2-18 Skill/script/reference sync fixtures | Block 2 | fixtures/skills/csv-quality; final-checks/reset tests | PASS |
| B2-19 Direct ngưỡng 8 | Block 2 | block-2/results/max-hours-8.json; execution metadata | PASS |
| B2-20 Direct ngưỡng 9 | Block 2 | block-2/results/max-hours-9.json; execution metadata | PASS |
| B2-21 Edge CSV/result/automated test | Block 2 | workload-edge.csv; results/edge-max-hours-0.json; test_workload.py:56 | PASS |
| B2-22 Agent-generated output | Block 2 | workspace/output/workload.md; live-results/threshold-8-workload.md, threshold-9-workload.md; write_file events | PASS |
| B2-23 Bốn required live branches | Block 2 | threshold-8/9, missing-threshold, missing-file-script mapped JSONL | PASS |
| B2-24 Analysis/trace vị trí/pytest | Block 2 | block-2/analysis.md; TRACE_VERIFICATION.md; 48/74 pytest passed | PASS |
| B2-25 Câu hỏi script/model/stale skill | Block 2 | block-2/analysis.md section 14 | PASS |

## Supplemental

PDF/DOCX và screenshots là trình bày bổ sung, không thay các file bắt buộc.
Security/ZIP checks được ghi riêng trong FINAL_AUDIT.md và verification/.
Required HTML groups: Block 1 24/24 PASS; Block 2 25/25 PASS.
