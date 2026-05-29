from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Chunk:

    chunk_id: str

    content: str

    section_number: str

    section_title: str

    source_file: str

    chunk_index: int

    token_count: int = 0

    page_start: Optional[int] = None

    page_end: Optional[int] = None

    metadata: dict = field(default_factory=dict)