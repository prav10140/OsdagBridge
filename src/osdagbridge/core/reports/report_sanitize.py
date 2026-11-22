# osdagbridge/core/reports/report_sanitize.py
"""Clean the design results before the report is written.

Problem seen in the v15 / v19 reports: the design has 3 girders, but results of an
EARLIER run (G4, G5, and cross-bracing pairs such as G4-G5) were still stored in
output_dict, so Table 5.30, the charts and other tables listed girders that do not
exist. The cause is stale per-girder data kept by the backend between consecutive
design runs.

prune_stale_girders() returns a deep copy of output_dict with every entry that
belongs to a girder number above the real number of girders removed. The live
backend dictionary is never modified.
"""
import copy
import logging
import re

logger = logging.getLogger(__name__)

_NAME = re.compile(r"^G(\d+)(?:-G(\d+))?$")        # "G4", "G4-G5"
_FLAT = re.compile(r"\.G(\d+)$")                    # "steeldesign.defl_live.G4"


def _n_girders(input_dict):
    try:
        from osdagbridge.core.utils.common import KEY_TS_NO_OF_GIRDERS
        return int(float(input_dict.get(KEY_TS_NO_OF_GIRDERS)))
    except Exception:
        return None


def _stale(key, n):
    """True when `key` refers to a girder number greater than n."""
    k = str(key)
    m = _NAME.match(k)
    if m:
        return max(int(g) for g in m.groups() if g) > n
    m = _FLAT.search(k)
    return bool(m and int(m.group(1)) > n)


def _prune(obj, n, counter):
    if isinstance(obj, dict):
        for k in [k for k in obj if _stale(k, n)]:
            del obj[k]
            counter[0] += 1
        for v in obj.values():
            _prune(v, n, counter)
    elif isinstance(obj, list):
        for v in obj:
            _prune(v, n, counter)


def prune_stale_girders(output_dict, input_dict):
    """Return a pruned deep copy of output_dict (or output_dict itself if the number
    of girders is unknown)."""
    n = _n_girders(input_dict or {})
    if not n or not output_dict:
        return output_dict
    try:
        cleaned = copy.deepcopy(output_dict)
    except Exception as exc:                      # un-copyable object: leave data alone
        logger.warning("Stale-girder clean-up skipped (%s)", exc)
        return output_dict
    counter = [0]
    _prune(cleaned, n, counter)
    if counter[0]:
        logger.warning("Report: removed %d result entries of girders above G%d "
                       "(stale data from an earlier design run)", counter[0], n)
    return cleaned