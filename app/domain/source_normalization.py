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
    "[3] IPC-6013B - Qualification and Performance Specification for Flexible Printed Boards.pdf": "IPC-6013B",
    "[2] NASA Workshop G - Printed Circuit Board Inspection and Quality Control.pdf": "NASA Workshop G",
    "[5] GSFC-STD-8001 - Standard Quality Assurance Requirements for Printed Circuit Boards.pdf": "GSFC-STD-8001",
    "[6] NASA-STD-8739.6B - Implementation Requirements for NASA Workmanship Standards.pdf": "NASA-STD-8739.6B",
}


def infer_applicable_standard_from_sources(sources: list[dict]) -> str:
    if not sources:
        return "unknown"

    first_source = sources[0].get("source_file", "")
    return SOURCE_STANDARD_MAP.get(first_source, "unknown")
