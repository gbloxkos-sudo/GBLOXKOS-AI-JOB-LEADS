"""Job finder orchestration (AppImage edition).

Priority:
1. Keyless public boards (RemoteOK / Remotive / WeWorkRemotely via MCP) - no API key
2. AI generation via Gemini (if GEMINI_API_KEY set) - optional cloud fallback
3. Local sample data - final fallback
4. Evaluation: Ollama (qwen2.5:3b) > Gemini > Heuristic - all offline-capable

No API key is ever required to search or rank.
"""

import logging
import os
import re
from typing import Any, Dict, List

try:
    from .gemini_provider import GeminiProvider
except Exception:
    GeminiProvider = None  # optional
from .main import fetch_jobs
from .ollama_provider import OllamaProvider

logger = logging.getLogger(__name__)

DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")


def heuristic_evaluate(job: Dict[str, Any], resume_text: str) -> Dict[str, Any]:
    """Offline keyword-overlap scoring. Always available, no AI needed."""
    desc = f"{job.get('title', '')} {job.get('description', job.get('summary', ''))}".lower()
    words = [w for w in re.findall(r"[a-z0-9+#.]{2,}", resume_text.lower()) if len(w) > 2]
    skills = [w for w in dict.fromkeys(words) if w in desc]
    total = max(len(set(words)), 1)
    score = min(95, int(len(set(skills)) / total * 400))  # scaled overlap
    score = max(5, min(95, score))
    top = ", ".join(sorted(set(skills))[:6]) or "no direct keyword overlap"
    return {"score": score, "reasoning": f"Heuristic match ({top}). Enable Ollama qwen2.5:3b for deeper scoring."}


def _get_evaluation_provider():
    """Get the best available AI provider for job EVALUATION (not generation).

    Priority:
    1. Ollama (if available and model pulled) - has evaluate, rank_jobs_batch
    2. Gemini (if API key configured) - has evaluate, rank_jobs_batch
    3. None (caller should use heuristic_evaluate)

    Returns:
        Provider instance with evaluate/rank_jobs_batch methods, or None
    """
    # Try Ollama first (local, no quota limits, default qwen2.5:3b)
    try:
        provider = OllamaProvider(model=os.getenv("OLLAMA_MODEL", DEFAULT_OLLAMA_MODEL))
        if provider.is_available():
            logger.info("Using Ollama provider for evaluation (%s)", provider.model)
            return provider
        else:
            logger.info("Ollama not available (model not pulled?), trying Gemini/heuristic")
    except Exception as e:
        logger.debug("Ollama provider unavailable: %s", e)

    # Try Gemini as optional fallback (only if key configured)
    if GeminiProvider is not None:
        try:
            provider = GeminiProvider()
            logger.info("Using Gemini provider for evaluation")
            return provider
        except Exception as e:
            logger.debug("Gemini provider unavailable: %s", e)

    logger.warning("No AI providers available - caller should use heuristic_evaluate()")
    return None


def _get_generation_provider():
    """Get provider for JOB GENERATION (creates leads from query).

    Only GeminiProvider supports this (via google_search tool).
    Returns provider or None.
    """
    if GeminiProvider is not None:
        try:
            provider = GeminiProvider()
            logger.info("Using Gemini provider for job generation")
            return provider
        except Exception as e:
            logger.debug("Gemini generation provider unavailable: %s", e)
    return None


def generate_job_leads(
    query: str,
    resume_text: str,
    count: int = 5,
    model: str | None = None,
    verbose: bool = False,
    evaluate: bool = False,
    use_mcp: bool = True,
) -> List[Dict[str, Any]]:
    """Generate job leads using MCP providers, Gemini, or local fallback.

    Priority:
    1. MCP providers (if use_mcp=True and MCPs available) - keyless
    2. Gemini provider (if API key configured) - cloud
    3. Local sample data (final fallback) - offline

    Args:
        query: Job search query.
        resume_text: Candidate's resume/profile text.
        count: Number of leads to return.
        model: Optional model name override (for Gemini).
        verbose: Print verbose diagnostics.
        evaluate: If True, score each job against the resume (0-100).
        use_mcp: If True, try MCP providers first (default: True).

    Returns a list of job dicts. On failure returns empty list.
    """
    leads: List[Dict[str, Any]] = []

    # 1. Try MCP providers first (keyless public APIs)
    if use_mcp:
        try:
            from .mcp_providers import generate_job_leads_via_mcp

            location = os.getenv("DEFAULT_LOCATION", "United States")
            count_per_mcp = int(os.getenv("JOBS_PER_MCP", str(count * 3)))

            logger.info(
                "Trying MCP providers (count=%d, per_provider=%d, location=%s)", count * 3, count_per_mcp, location
            )
            leads = generate_job_leads_via_mcp(
                query=query, count=count * 3, count_per_provider=count_per_mcp, location=location
            )

            if leads:
                logger.info("MCP providers returned %d leads", len(leads))
                # Evaluate if requested - use BATCH ranking for speed
                if evaluate:
                    _evaluate_with_fallback(leads, resume_text, count, verbose)
                return leads
            else:
                print("job_finder: No results from MCP providers, trying Gemini generation...")

        except Exception as e:
            if verbose:
                import traceback
                print(f"job_finder: MCP providers failed: {e}")
                traceback.print_exc()
            print("job_finder: MCP unavailable, falling back to Gemini generation")

    # 2. Try Gemini for GENERATION (requires API key)
    gen_provider = _get_generation_provider()
    if gen_provider:
        try:
            leads = gen_provider.generate_job_leads(query, resume_text, count=count, model=model, verbose=verbose)
            print(f"job_finder: {type(gen_provider).__name__} generated {len(leads)} leads")
            if leads:
                if evaluate:
                    _evaluate_with_fallback(leads, resume_text, count, verbose)
                return leads
            else:
                print("job_finder: AI generation returned 0 leads, using local fallback")
        except Exception as e:
            if os.getenv("VERBOSE") or verbose:
                import traceback
                print("job_finder: Exception while calling AI generation:", e)
                traceback.print_exc()
            print("job_finder: AI generation failed, using local fallback")
    elif verbose:
        print("job_finder: no generation provider (no GEMINI_API_KEY); local fallback")

    # 3. Fallback: use simple local search (keyless, offline)
    sample = fetch_jobs(query)
    leads = []
    for j in sample[:count]:
        leads.append({
            "title": j.get("title"),
            "company": j.get("company"),
            "location": j.get("location"),
            "summary": j.get("description"),
            "link": j.get("link", ""),
            "source": "Local",
        })
    print(f"job_finder: Fallback returned {len(leads)} leads")
    if evaluate:
        _evaluate_with_fallback(leads, resume_text, count, verbose)
    return leads


def _evaluate_with_fallback(leads: List[Dict[str, Any]], resume_text: str, top_n: int, verbose: bool = False):
    """Evaluate leads with best available provider, fallback to heuristic."""
    try:
        provider = _get_evaluation_provider()
        if provider and hasattr(provider, "rank_jobs_batch"):
            logger.info("Batch ranking %d jobs with %s...", len(leads), type(provider).__name__)
            ranked = provider.rank_jobs_batch(leads, resume_text, top_n=top_n)
            # Ensure all returned have score/reasoning
            for lead in ranked:
                if "score" not in lead:
                    lead["score"] = 50
                if "reasoning" not in lead:
                    lead["reasoning"] = "Ranked by AI"
            leads[:] = ranked
            logger.info("Ranked and filtered to top %d jobs", len(leads))
            return
    except Exception as e:
        if verbose:
            print(f"job_finder: Batch ranking unavailable: {e}")

    # Heuristic fallback - never hard-fail
    logger.warning("Using heuristic evaluation fallback")
    for lead in leads:
        ev = heuristic_evaluate(
            {"title": lead.get("title", ""), "description": lead.get("summary", "")},
            resume_text,
        )
        lead["score"] = ev["score"]
        lead["reasoning"] = ev["reasoning"]
    leads.sort(key=lambda j: j.get("score", 0), reverse=True)
    del leads[top_n:]


def _evaluate_leads(
    leads: List[Dict[str, Any]],
    resume_text: str,
    provider,  # OllamaProvider | GeminiProvider
    verbose: bool = False,
) -> List[Dict[str, Any]]:
    """Evaluate each lead against resume and add score/reasoning.

    Args:
        leads: List of job leads to evaluate.
        resume_text: Candidate's resume text for matching.
        provider: Provider with evaluate() method.
        verbose: If True, print diagnostic information.

    Returns:
        List of evaluated leads with score and reasoning fields added.
    """
    evaluated = []
    for lead in leads:
        try:
            job_dict = {
                "title": lead.get("title", ""),
                "company": lead.get("company", ""),
                "location": lead.get("location", ""),
                "description": lead.get("summary", ""),
            }
            evaluation = provider.evaluate(job_dict, resume_text)
            lead["score"] = evaluation.get("score", 0)
            lead["reasoning"] = evaluation.get("reasoning", "")
        except Exception as e:
            if verbose:
                print(f"job_finder: evaluation failed for {lead.get('title', '?')}: {e}")
            lead["score"] = 50
            lead["reasoning"] = "Evaluation unavailable."
        evaluated.append(lead)
    return evaluated


def save_to_file(leads: List[Dict[str, Any]], path: str) -> None:
    """Save leads to JSON file (creates or overwrites)."""
    import json

    with open(path, "w", encoding="utf-8") as fh:
        json.dump(leads, fh, indent=2)
    print(f"job_finder: saved {len(leads)} leads to {path}")
