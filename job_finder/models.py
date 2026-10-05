from dataclasses import dataclass


@dataclass
class Job:
    source: str
    company: str
    title: str
    location: str
    description: str
    apply_url: str
    salary_min: object = ""
    salary_max: object = ""
    posted_date: str = ""

    @property
    def dedupe_key(self) -> str:
        """Apply URL when available, else company|title|location."""
        key = self.apply_url or f"{self.company}|{self.title}|{self.location}"
        return key.lower().strip()


@dataclass
class RunLog:
    timestamp: str
    source: str
    status: str
    count: int
    error: str = ""
