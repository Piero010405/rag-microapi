"""
Defect knowledge base for printed board manufacturing defects, structured to align with IPC 
standards and engineering severity assessments. Each defect entry includes a canonical name, IPC 
classification, severity level, detailed description, engineering justification, query aliases 
for flexible search, recommended standard targets for inspection criteria, and the applicable 
inspection scope.
"""
DEFECT_KNOWLEDGE = {
    "short_circuit": {
        "canonical_name": "short circuit",
        "ipc_family": "Conductive Pattern / Spacing",
        "ipc_basis": "Nonconforming",
        "derived_severity": "critical",
        "description": "Unintended electrical connection between conductors.",
        "engineering_justification": "Violates minimum electrical spacing and may cause direct functional failure.",
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
        "ipc_family": "Conductive Pattern / Definition",
        "ipc_basis": "Acceptable → Nonconforming",
        "derived_severity": "medium",
        "description": "Thin copper protrusion extending from a conductor.",
        "engineering_justification": "May reduce spacing and become critical depending on proximity to adjacent conductors.",
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
        "ipc_family": "Conductive Pattern / Residual Metal",
        "ipc_basis": "Process Indicator → Nonconforming",
        "derived_severity": "medium",
        "description": "Unwanted isolated copper remaining after etching.",
        "engineering_justification": "Risk depends on size and proximity to active conductive features.",
        "query_aliases": [
            "spurious copper",
            "residual copper",
            "extraneous copper",
            "unwanted copper",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "open_circuit": {
        "canonical_name": "open circuit",
        "ipc_family": "Conductive Pattern / Continuity",
        "ipc_basis": "Nonconforming",
        "derived_severity": "critical",
        "description": "Break in the intended conductive path.",
        "engineering_justification": "Causes loss of electrical continuity and direct functional failure.",
        "query_aliases": [
            "open circuit",
            "electrical open",
            "conductor discontinuity",
            "broken conductive path",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012", "NASA Workshop G"],
        "inspection_scope": "printed_board",
    },
    "mouse_bite": {
        "canonical_name": "mouse bite",
        "ipc_family": "Conductive Pattern / Dimensional Integrity",
        "ipc_basis": "Nonconforming (threshold-based)",
        "derived_severity": "high",
        "description": "Irregular conductor edge defect causing width reduction.",
        "engineering_justification": "May reduce current-carrying capacity and reliability.",
        "query_aliases": [
            "mouse bite",
            "edge breakout",
            "edge defect",
            "irregular board edge damage",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "hole_breakout": {
        "canonical_name": "hole breakout",
        "ipc_family": "Holes / Annular Ring Integrity",
        "ipc_basis": "Nonconforming (Class-dependent)",
        "derived_severity": "high",
        "description": "Hole not fully surrounded by copper annular ring.",
        "engineering_justification": "Weakens mechanical/electrical reliability of plated holes and vias.",
        "query_aliases": [
            "hole breakout",
            "annular ring breakout",
            "insufficient annular ring",
        ],
        "recommended_standard_targets": ["IPC-A-600", "IPC-6012"],
        "inspection_scope": "printed_board",
    },
    "conductor_scratch": {
        "canonical_name": "conductor scratch",
        "ipc_family": "Conductive Pattern / Surface Imperfection",
        "ipc_basis": "Process Indicator",
        "derived_severity": "low",
        "description": "Surface damage affecting the conductor finish or top layer.",
        "engineering_justification": "Often cosmetic unless it significantly reduces thickness or exposes base material.",
        "query_aliases": [
            "conductor scratch",
            "scratch on conductor",
            "surface damage conductor",
        ],
        "recommended_standard_targets": ["IPC-A-600"],
        "inspection_scope": "printed_board",
    },
    "conductor_foreign_object": {
        "canonical_name": "conductor foreign object",
        "ipc_family": "Conductive Pattern / Contamination",
        "ipc_basis": "Nonconforming (if conductive)",
        "derived_severity": "high",
        "description": "Foreign material present on or near a conductive feature.",
        "engineering_justification": "May induce bridging, corrosion, or unintended conductive paths.",
        "query_aliases": [
            "foreign object conductor",
            "conductive contamination",
            "foreign material on conductor",
        ],
        "recommended_standard_targets": ["IPC-A-600", "NASA Workshop G"],
        "inspection_scope": "printed_board",
    },
    "base_material_foreign_object": {
        "canonical_name": "base material foreign object",
        "ipc_family": "Base Material / Subsurface Inclusion",
        "ipc_basis": "Acceptable → Nonconforming",
        "derived_severity": "low",
        "description": "Foreign inclusion embedded in the base material.",
        "engineering_justification": "Impact depends on size, transparency, and distance to conductive features.",
        "query_aliases": [
            "foreign inclusion base material",
            "subsurface inclusion",
            "embedded foreign object",
        ],
        "recommended_standard_targets": ["IPC-A-600"],
        "inspection_scope": "printed_board",
    },
}


def get_defect_knowledge(defect_class: str) -> dict:
    """
    Get the knowledge for a given defect class.
    """
    key = defect_class.strip().lower().replace(" ", "_")
    return DEFECT_KNOWLEDGE.get(
        key,
        {
            "canonical_name": defect_class.replace("_", " ").lower(),
            "ipc_family": "Unknown",
            "ipc_basis": "Unknown",
            "derived_severity": "unknown",
            "description": defect_class.replace("_", " ").lower(),
            "engineering_justification": "No engineering justification available.",
            "query_aliases": [defect_class.replace("_", " ").lower()],
            "recommended_standard_targets": ["IPC-A-600"],
            "inspection_scope": "printed_board",
        },
    )
