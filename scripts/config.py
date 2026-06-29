from dataclasses import dataclass, field


@dataclass
class Config:
    # Research
    topic: str = ""

    # Discovery
    platforms: list[str] = field(default_factory=list)
    candidate_limit: int = 20
    country: str = ""
    language: str = "en"
    search_keywords: list[str] = field(default_factory=list)
    required_platforms: list[str] = field(default_factory=list)

    # Output
    output_folder: str = "research"
    output_format: str = "json"

    # APIs
    apis: list[str] = field(default_factory=list)
    api_keys: dict = field(default_factory=dict)

    # Evaluation
    evaluation_criteria: list[str] = field(default_factory=list)