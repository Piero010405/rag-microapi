DEFECT_NORMALIZATION = {
    "open_circuit": {
        "canonical_name": "open circuit",
        "query_aliases": [
            "open circuit",
            "electrical open",
            "conductor discontinuity",
            "broken conductive path",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012", "NASA Workshop G"],
        "inspection_scope": "printed_board",
    },
    "short_circuit": {
        "canonical_name": "short circuit",
        "query_aliases": [
            "short circuit",
            "electrical short",
            "unintended conductive connection",
            "bridging between conductors",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012", "NASA Workshop G"],
        "inspection_scope": "printed_board",
    },
    "spur": {
        "canonical_name": "spur",
        "query_aliases": [
            "spur",
            "conductive projection",
            "copper projection",
            "protruding conductor defect",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "spurious_copper": {
        "canonical_name": "spurious copper",
        "query_aliases": [
            "spurious copper",
            "residual copper",
            "extraneous copper",
            "unwanted copper",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "mouse_bite": {
        "canonical_name": "mouse bite",
        "query_aliases": [
            "mouse bite",
            "edge breakout",
            "edge defect",
            "irregular board edge damage",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "pin_hole": {
        "canonical_name": "pin hole",
        "query_aliases": [
            "pin hole",
            "pinhole",
            "small hole defect",
            "void-like surface defect",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "missing_hole": {
        "canonical_name": "missing hole",
        "query_aliases": [
            "missing hole",
            "absent drilled hole",
            "missing drilled feature",
            "hole omission",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "wrong_hole": {
        "canonical_name": "wrong hole",
        "query_aliases": [
            "wrong hole",
            "mislocated hole",
            "incorrect drilled hole",
            "hole dimensional defect",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "break": {
        "canonical_name": "break",
        "query_aliases": [
            "break",
            "fracture",
            "broken conductor",
            "structural break",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012", "NASA Workshop G"],
        "inspection_scope": "printed_board",
    },
}


def normalize_defect_class(defect_class: str) -> dict:
    key = defect_class.strip().lower().replace(" ", "_")
    return DEFECT_NORMALIZATION.get(
        key,
        {
            "canonical_name": defect_class.replace("_", " ").lower(),
            "query_aliases": [defect_class.replace("_", " ").lower()],
            "recommended_standard_targets": ["IPC-A-600"],
            "inspection_scope": "printed_board",
        },
    )
