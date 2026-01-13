import asyncio
from typing import List, Dict
from operator import itemgetter
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import (
    RunnableParallel,
    RunnableLambda,
)

from api.app.db import logger
from api.app.util.settings import settings
from api.app.util.base_classes import ComplianceAnswer, ComplianceResponse
from api.app.db.chromadb_adapter import ChromaDBAdapter as vector_db_adapter


class ComplianceChain:

    def __init__(self, filename: str):
        self.filename = filename
        self.vector_adapter = vector_db_adapter()
        self.llm = AzureChatOpenAI(
            azure_endpoint=settings.azure_endpoint,
            azure_deployment=settings.azure_deployment,
            api_version=settings.azure_api_version,
            api_key=settings.azure_api_key,
            max_completion_tokens=8000,
            # temperature=0.4,
            max_retries=1,
        ).with_structured_output(ComplianceAnswer)

        self.prompt = ChatPromptTemplate.from_template(
            """You are an expert compliance analyst. Given relevant pages from a contract and compliance requirement, you need to determine the level of compliance"
            You need to define the following based on the contract excerpts:
            * State of compliance - whether the contract is fully, partial or non compliant
            * Confidence - how confident (score out of hundred) are you about the compliance state
            * Relevant quotes - short quotes from the contract which are relevant to the compliance state
            * Rationale - concise single sentence reasoning for the assigned compliance state
            
            
            Compliance requirement: {requirement}
            
            Contract pages: {pages}"""
        )

        self.comp_requirements = [
            {
                "requirement": "**Password Management.** The contract must require a documented password standard covering password length/strength, prohibition of default and known-compromised passwords, secure storage (no plaintext; salted hashing if stored), brute-force protections (lockout/rate limiting), prohibition on password sharing, vaulting of privileged credentials/recovery codes, and time-based rotation for break-glass credentials. **Based on the contract language and exhibits, what is the compliance state for Password Management?**",
                "metadata": {"keywords": "Password Management", "filename": filename},
            },
            {
                "requirement": "**IT Asset Management.** The contract must require an in-scope asset inventory (including cloud accounts/subscriptions, workloads, databases, security tooling), define minimum inventory fields, require at least quarterly reconciliation/review, and require secure configuration baselines with drift remediation and prohibition of insecure defaults. **Based on the contract language and exhibits, what is the compliance state for IT Asset Management?**",
                "metadata": {"keywords": "IT Asset Management", "filename": filename},
            },
            {
                "requirement": "**Security Training & Background Checks.** The contract must require security awareness training on hire and at least annually, and background screening for personnel with access to Company Data to the extent permitted by law, including maintaining a screening policy and attestation/evidence. **Based on the contract language and exhibits, what is the compliance state for Security Training and Background Checks?**",
                "metadata": {
                    "keywords": "Security Training & Background Checks",
                    "filename": filename,
                },
            },
            {
                "requirement": "**Data in Transit Encryption.** The contract must require encryption of Company Data in transit using TLS 1.2+ (preferably TLS 1.3 where feasible) for Company-to-Service traffic, administrative access pathways, and applicable Service-to-Subprocessor transfers, with certificate management and avoidance of insecure cipher suites. **Based on the contract language and exhibits, what is the compliance state for Data in Transit Encryption?**",
                "metadata": {
                    "keywords": "Data in Transit Encryption",
                    "filename": filename,
                },
            },
            {
                "requirement": "**Network Authentication & Authorization Protocols.** The contract must specify the authentication mechanisms (e.g., SAML SSO for users, OAuth/token-based for APIs), require MFA for privileged/production access, require secure admin pathways (bastion/secure gateway) with session logging, and require RBAC authorization. **Based on the contract language and exhibits, what is the compliance state for Network Authentication and Authorization Protocols?**",
                "metadata": {
                    "keywords": "Network Authentication & Authorization Protocols",
                    "filename": filename,
                },
            },
        ]

        pages = itemgetter("metadata") | RunnableLambda(self._context_retriever)
        answer_chain = (
            RunnableParallel(
                {
                    "pages": pages,
                    "requirement": itemgetter("requirement"),
                }
            )
            | self.prompt
            | self.llm
        )
        self.chain = RunnableParallel(
            {
                "answer": answer_chain,
                "requirement_name": RunnableLambda(lambda x: x["metadata"]["keywords"]),
            }
        )

    def _context_retriever(self, data: Dict) -> str:
        filename = data["filename"]
        keywords = data["keywords"]
        page_list = self.vector_adapter.get_pages(filename, keywords, n=5)

        logger.info("Number of pages for file %s: %d" , filename, len(page_list))
        logger.debug("Chunk ids: %s", " ,".join([page["id"] for page in page_list]))
        logger.debug(
            "Chunk distances: %s", " ,".join([page["id"] for page in page_list])
        )

        out = [page["text"] for page in page_list]
        return "\n\n".join(out)

    async def invoke(self) -> List[ComplianceResponse]:
        llm_responses = await self.chain.abatch(self.comp_requirements)
        out = []
        for response in llm_responses:
            out.append(
                ComplianceResponse(
                    pdf_name=self.filename,
                    compliance_requirement=response["requirement_name"],
                    compliance_state=response["answer"].compliance_state,
                    confidence=response["answer"].confidence,
                    relevant_quotes=response["answer"].relevant_quotes,
                    rationale=response["answer"].rationale,
                )
            )
        return out
