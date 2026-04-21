"""
Source normalization mapping for standardizing the names of the source documents. This mapping is 
used to ensure that different variations of the same source document are recognized as the same 
standard, which helps in maintaining consistency in the analysis and reporting processes. 
The keys in the mapping represent the original names of the source documents, while the values 
represent the standardized names that will be used in the system. This normalization process 
is crucial for accurate referencing and retrieval of information related to the standards being 
analyzed.
"""
SOURCE_STANDARD_MAP = {
    "ipc-a-6010.pdf": "IPC-A-610F",
    "[1] IPC-A-600M - Acceptability of Printed Boards.pdf": "IPC-A-600M",
    "ipc-6012f.pdf": "IPC-6012F",
    "[3] IPC-6013B - Qualification and Performance Specification for Flexible Printed Boards.pdf": (
        "IPC-6013B"
    ),
    "[2] NASA Workshop G - Printed Circuit Board Inspection and Quality Control.pdf": (
        "NASA Workshop G"
    ),
    "[5] GSFC-STD-8001 - Standard Quality Assurance Requirements for Printed Circuit Boards.pdf": (
        "GSFC-STD-8001"
    ),
    "[6] NASA-STD-8739.6B - Implementation Requirements for NASA Workmanship Standards.pdf": (
        "NASA-STD-8739.6B"
    ),
}


def infer_applicable_standard_from_sources(
    sources,
    recommended_standard_target: str | None = None,
) -> str:
    """
    Infer the applicable standard from a list of sources. If a recommended standard target is 
    provided, it will be returned directly. Otherwise, the function will analyze the sources to 
    determine the most frequently occurring standardized name based on the SOURCE_STANDARD_MAP. If 
    no sources are provided or if none of the sources match the mapping, it will return "unknown".
    """
    if recommended_standard_target:
        return recommended_standard_target

    if not sources:
        return "unknown"

    counts: dict[str, int] = {}

    for src in sources:
        if hasattr(src, "source_file"):
            source_file = src.source_file
        elif isinstance(src, dict):
            source_file = src.get("source_file", "")
        else:
            source_file = ""

        normalized = SOURCE_STANDARD_MAP.get(source_file, "unknown")
        counts[normalized] = counts.get(normalized, 0) + 1

    if not counts:
        return "unknown"

    return max(counts.items(), key=lambda x: x[1])[0]
