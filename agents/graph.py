"""LangGraph wiring: Attacker -> Target -> Judge -> Defender loop."""
from typing import TypedDict, Annotated
import operator
from langgraph.graph import StateGraph, START, END

from .attacker import generate_probe
from .target import call_target
from .judge import evaluate
from .defender import harden


class SecurityTestState(TypedDict):
    system_prompt: str
    categories: list
    total_rounds: int
    round: int
    history: Annotated[list, operator.add]
    failures: Annotated[list, operator.add]
    prompt_patches: Annotated[list, operator.add]   # ← NEW: tracks v1→v2→v3 patches
    current_probe: str
    current_response: str
    current_verdict: dict
    finished: bool


def _current_category(state):
    idx = (state["round"] - 1) % len(state["categories"])
    return state["categories"][idx]


def attacker_node(state):
    category = _current_category(state)
    # Collect ALL past probes (not just same-category) to avoid repeats
    past_probes = [h["probe"] for h in state["history"] if h.get("probe")]
    probe = generate_probe(category, history=past_probes)
    return {"current_probe": probe}


def target_node(state):
    response = call_target(state["system_prompt"], state["current_probe"])
    return {"current_response": response}


def judge_node(state):
    verdict = evaluate(state["current_probe"], state["current_response"])
    category = _current_category(state)
    record = {
        "round": state["round"],
        "category": category,
        "probe": state["current_probe"],
        "response": state["current_response"],
        "verdict": verdict["verdict"],
        "severity": verdict["severity"],
        "reason": verdict["reason"],
    }
    failures = [record] if verdict["verdict"] == "FAIL" else []
    return {"current_verdict": verdict, "history": [record], "failures": failures}


def defender_node(state):
    old_prompt = state["system_prompt"]
    new_prompt = harden(old_prompt, state["failures"])

    current_round = state.get("round", 1)
    total = state.get("total_rounds", 5)
    next_round = current_round + 1
    finished = next_round > total

    # Only record a patch if the prompt actually changed
    patch_record = None
    if new_prompt and new_prompt.strip() != old_prompt.strip():
        patch_record = {
            "round": current_round,
            "category": _current_category(state),
            "old_prompt": old_prompt,
            "new_prompt": new_prompt,
        }

    return {
        "system_prompt": new_prompt,
        "round": next_round,
        "finished": finished,
        "prompt_patches": [patch_record] if patch_record else [],
    }


def _route_after_defender(state):
    current_round = state.get("round", 1)
    total = state.get("total_rounds", 5)
    if state.get("finished") or current_round > total:
        return END
    return "attacker"


def build_graph():
    g = StateGraph(SecurityTestState)
    g.add_node("attacker", attacker_node)
    g.add_node("target", target_node)
    g.add_node("judge", judge_node)
    g.add_node("defender", defender_node)

    g.add_edge(START, "attacker")
    g.add_edge("attacker", "target")
    g.add_edge("target", "judge")
    g.add_edge("judge", "defender")
    g.add_conditional_edges(
        "defender",
        _route_after_defender,
        {"attacker": "attacker", END: END},
    )
    return g.compile()
