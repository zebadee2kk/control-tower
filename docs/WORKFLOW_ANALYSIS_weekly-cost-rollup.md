# Workflow Analysis: weekly-cost-rollup.yml

## Line-by-Line Findings
- L23-28: Reads max 100 issues only.
- L37: Regex only supports integer `Budget: Xh, £Y` format.
- L43: Hard-coded overrun threshold (`>100`) with no policy source.
- L54-60: Creates report issue every run without dedupe/close strategy.

## Risks
1. Under-counts cost when issue template format drifts.
2. False confidence from partial data and silent parse failures.
3. Report proliferation over time.

## Security
- Low confidentiality risk.
- Integrity risk through malformed body poisoning metrics.

## Recommendation
- Structured budget fields (YAML front matter or issue form fields) + strict parser with validation stats.
