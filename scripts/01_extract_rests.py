#!/usr/bin/env python3
"""
Extract rest sequences (inactive segments) from two JSON files.

Outputs:
- rests_* as list of durations in eighth-note units
- rest_intervals_* as list of [start, end] in quarterLength units (or whatever unit your JSON uses)

Heuristics:
1) If explicit rest events exist -> use them
2) Else infer rests as gaps between active events (end_i -> onset_{i+1})
3) Coalesce contiguous/overlapping rest intervals

Optionally validates Nidi panel-1 against an expected 18-rest sequence.
"""

from __future__ import annotations

import argparse
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

EPS = 1e-9

EXPECTED_NIDI_PANEL1_EIGHTH = [
    3, 2.5, 1, 3.5, 1, 4, 1.5, 0.5, 1.5, 3, 2.5, 0.5, 3.5, 1, 4, 1.5, 0.5, 0.5
]


def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def find_event_list(obj: Any) -> Optional[List[Dict[str, Any]]]:
    """
    Try to locate a list[dict] representing events inside an arbitrary JSON structure.
    """
    if isinstance(obj, list) and (len(obj) == 0 or isinstance(obj[0], dict)):
        return obj

    if isinstance(obj, dict):
        for key in ["events", "event_list", "items", "notes", "data", "sequence", "segments"]:
            v = obj.get(key)
            if isinstance(v, list) and (len(v) == 0 or isinstance(v[0], dict)):
                return v
        for v in obj.values():
            if isinstance(v, (dict, list)):
                ev = find_event_list(v)
                if ev is not None:
                    return ev
    return None


def first_present(d: Dict[str, Any], keys: Iterable[str]) -> Optional[Any]:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def to_float(x: Any) -> Optional[float]:
    if x is None:
        return None
    try:
        return float(x)
    except Exception:
        return None


def is_rest_event(ev: Dict[str, Any]) -> bool:
    for k in ["is_rest", "isRest", "rest", "is_silence", "silence"]:
        if k in ev and bool(ev[k]) is True:
            return True

    t = first_present(ev, ["type", "kind", "event_type", "eventType", "name"])
    if isinstance(t, str) and "rest" in t.lower():
        return True

    pitch_like = first_present(ev, ["pitch_midi", "pitchMidi", "pitch", "pc", "pitch_class", "pitchClass"])
    pitches = first_present(ev, ["pitches", "midi", "midis"])
    if pitch_like is None:
        if isinstance(pitches, list) and len(pitches) == 0:
            return True
    return False


def get_onset(ev: Dict[str, Any]) -> Optional[float]:
    return to_float(first_present(ev, ["offset", "off", "onset", "start", "t", "time", "offset_q", "onset_q", "start_q"]))


def get_dur(ev: Dict[str, Any]) -> Optional[float]:
    dur = to_float(first_present(ev, ["dur_q", "duration_q", "dur", "duration", "ql", "quarterLength", "quarter_length"]))
    if dur is not None:
        return dur

    dur8 = to_float(first_present(ev, ["dur_8", "duration_8", "eighth", "eighths"]))
    if dur8 is not None:
        return dur8 / 2.0

    return None


def coalesce_intervals(intervals: List[Tuple[float, float]], eps: float = EPS) -> List[Tuple[float, float]]:
    if not intervals:
        return []
    intervals = sorted(intervals, key=lambda x: (x[0], x[1]))
    out = [intervals[0]]
    for s, e in intervals[1:]:
        ps, pe = out[-1]
        if s <= pe + eps:
            out[-1] = (ps, max(pe, e))
        else:
            out.append((s, e))
    return out


def extract_rest_intervals(events: List[Dict[str, Any]], require_explicit: bool = False) -> List[Tuple[float, float]]:
    """
    Return rest intervals as (start, end) in quarterLength units (or consistent unit).
    """
    rest_intervals: List[Tuple[float, float]] = []

    # 1) explicit rests
    for ev in events:
        if not isinstance(ev, dict):
            continue
        if is_rest_event(ev):
            onset = get_onset(ev)
            dur = get_dur(ev)
            if onset is None or dur is None:
                continue
            if dur > EPS:
                rest_intervals.append((onset, onset + dur))

    rest_intervals = coalesce_intervals(rest_intervals)

    if rest_intervals or require_explicit:
        return rest_intervals

    # 2) infer rests as gaps between active events
    active_spans: List[Tuple[float, float]] = []
    for ev in events:
        if not isinstance(ev, dict):
            continue
        if is_rest_event(ev):
            continue
        onset = get_onset(ev)
        dur = get_dur(ev)
        if onset is None or dur is None:
            continue
        if dur < 0:
            continue
        active_spans.append((onset, onset + dur))

    if not active_spans:
        return []

    active_spans = coalesce_intervals(active_spans)

    inferred: List[Tuple[float, float]] = []
    for (_s1, e1), (s2, _e2) in zip(active_spans, active_spans[1:]):
        gap = s2 - e1
        if gap > EPS:
            inferred.append((e1, s2))

    return coalesce_intervals(inferred)


def intervals_to_eighth_durations(rest_intervals_q: List[Tuple[float, float]]) -> List[float]:
    return [round((e - s) * 2.0, 6) for s, e in rest_intervals_q]


def validate_expected(label: str, got: List[float], expected: List[float]) -> None:
    if len(got) != len(expected):
        print(f"[WARN] {label}: got {len(got)} rests, expected {len(expected)}.")
    n = min(len(got), len(expected))
    max_err = max((abs(got[i] - expected[i]) for i in range(n)), default=0.0)
    print(f"[CHECK] {label}: max prefix abs error (eighth units) = {max_err:.6f}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lumen", required=True, help="Path to Lumen JSON (features.json or equivalent)")
    ap.add_argument("--nidi", required=True, help="Path to Nidi panel-1 JSON (features.json or equivalent)")
    ap.add_argument("--out", default=None, help="Optional output JSON path to save results")
    ap.add_argument("--require-explicit", action="store_true",
                    help="If set, do NOT infer rests from gaps; only accept explicit rest events.")
    ap.add_argument("--check-nidi-panel1", action="store_true",
                    help="Validate Nidi rests against the expected 18-rest sequence.")
    args = ap.parse_args()

    lumen_obj = load_json(args.lumen)
    nidi_obj = load_json(args.nidi)

    lumen_events = find_event_list(lumen_obj)
    nidi_events = find_event_list(nidi_obj)

    if lumen_events is None:
        raise SystemExit("Could not find an event list in Lumen JSON.")
    if nidi_events is None:
        raise SystemExit("Could not find an event list in Nidi JSON.")

    lumen_rest_intervals = extract_rest_intervals(lumen_events, require_explicit=args.require_explicit)
    nidi_rest_intervals = extract_rest_intervals(nidi_events, require_explicit=args.require_explicit)

    rests_lumen = intervals_to_eighth_durations(lumen_rest_intervals)
    rests_nidi = intervals_to_eighth_durations(nidi_rest_intervals)

    print("rests_lumen =", rests_lumen)
    print("rests_nidi  =", rests_nidi)
    print(f"[INFO] Lumen: {len(rests_lumen)} rests (coalesced)")
    print(f"[INFO] Nidi : {len(rests_nidi)} rests (coalesced)")

    if args.check_nidi_panel1:
        validate_expected("Nidi panel 1", rests_nidi, EXPECTED_NIDI_PANEL1_EIGHTH)

    payload = {
        "lumen": {
            "rests_eighth": rests_lumen,
            "rest_intervals_quarter": [[round(s, 6), round(e, 6)] for s, e in lumen_rest_intervals],
        },
        "nidi": {
            "rests_eighth": rests_nidi,
            "rest_intervals_quarter": [[round(s, 6), round(e, 6)] for s, e in nidi_rest_intervals],
        },
    }

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        print(f"[OK] Saved -> {args.out}")


if __name__ == "__main__":
    main()
