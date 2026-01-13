from enum import Enum
from typing import Annotated, List

from pydantic import BaseModel, Field


class ComplianceStateEnum(str, Enum):
    full = "fully_compliant"
    partial = "partially_compliant"
    non = "non__compliant"


class ComplianceAnswer(BaseModel):
    compliance_state: ComplianceStateEnum = Field(
        description="Level of compliance of the contract"
    )
    confidence: Annotated[int, Field(ge=0, le=100)] = Field(
        description="Level of confidence about the compliance state (out of 100)"
    )
    relevant_quotes: List[str] = Field(
        description="A list of quotes excerpts relevant to the compliance", max_length=4
    )
    rationale: str = Field(
        description="Short rationale behind the assigned compliance state"
    )


class ComplianceResponse(BaseModel):
    pdf_name: str
    compliance_requirement: str
    compliance_state: ComplianceStateEnum
    confidence: Annotated[int, Field(ge=0, le=100)]
    relevant_quotes: List[str]
    rationale: str
