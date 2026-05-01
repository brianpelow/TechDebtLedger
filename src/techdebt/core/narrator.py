"""AI-powered tech debt narrative generation."""

from __future__ import annotations

import os
from techdebt.models.debt import DebtSummary


def generate_debt_narrative(summary: DebtSummary, industry: str = "fintech") -> str:
    """Generate an executive tech debt narrative using Claude."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return _fallback_narrative(summary, industry)

    try:
        from openai import OpenAI
        client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)

        prompt = f"""You are an engineering director presenting a tech debt assessment to leadership in a {industry} company.

Repository: {summary.repo_name}
Debt score: {summary.debt_score}/100 (higher = more debt)
Total debt items: {summary.total_items}
Critical: {summary.critical_items} | High: {summary.high_items} | Medium: {summary.medium_items} | Low: {summary.low_items}
Complexity hotspots: {summary.complexity_hotspots}
Annotated debt items (TODO/FIXME): {summary.todo_count}
Stale dependencies: {summary.stale_dependencies}
Estimated remediation: {summary.estimated_remediation_hours} hours

Write a 3-paragraph executive summary that:
1. States the overall debt posture and what it means for the business
2. Identifies the highest-priority items and their risk implications for a {industry} regulated environment
3. Recommends a remediation approach with timeline and resource estimates

Use language appropriate for engineering leadership in a regulated {industry} environment.
Be specific, practical, and connect debt to delivery risk and compliance implications."""

        message = client.chat.completions.create(
            model="meta-llama/llama-3.1-8b-instruct:free",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )
        return message.choices[0].message.content

    except Exception:
        return _fallback_narrative(summary, industry)


def _fallback_narrative(summary: DebtSummary, industry: str) -> str:
    risk = "critical" if summary.debt_score >= 70 else "elevated" if summary.debt_score >= 40 else "manageable"
    return f"""## Tech Debt Assessment â€” {summary.repo_name}

**Overall debt posture is {risk}** with a debt score of {summary.debt_score}/100.
The codebase contains {summary.total_items} debt items requiring approximately
{summary.estimated_remediation_hours} hours of remediation effort.

{"**Immediate action required**: " + str(summary.critical_items) + " critical items were identified that pose significant delivery and compliance risk." if summary.critical_items > 0 else "No critical debt items were identified."}
{summary.complexity_hotspots} complexity hotspots increase incident blast radius and slow onboarding.
{summary.stale_dependencies} stale dependencies may carry unpatched CVEs â€” a compliance risk in {industry} environments.

**Recommended approach**: Address critical and high severity items in the next sprint ({summary.critical_items + summary.high_items} items, ~{round((summary.critical_items * 8 + summary.high_items * 4), 0)} hours).
Schedule medium severity items over the following two sprints. Establish a debt budget of 20% of engineering capacity to prevent accumulation.
"""