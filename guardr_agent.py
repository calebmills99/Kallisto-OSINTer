#!/usr/bin/env python3
"""
Guardr: Autonomous OSINT Agent System
Deterministic Plan → Execute → Review → Adjust (PERA) cycles
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json

from src.config import load_config
from src.llm.llm_client import LLMClient
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PhaseStatus(Enum):
    """Status of a PERA cycle phase"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolType(Enum):
    """Available OSINT tools"""
    WEB_SEARCH = "web_search"
    SOCIAL_LOOKUP = "social_lookup"
    IMAGE_SEARCH = "image_search"
    BREACH_CHECK = "breach_check"
    PHONE_LOOKUP = "phone_lookup"
    ADDRESS_LOOKUP = "address_lookup"


@dataclass
class InvestigationPlan:
    """Structured investigation plan from Plan phase"""
    objective: str
    sub_queries: List[str] = field(default_factory=list)
    tools_required: List[ToolType] = field(default_factory=list)
    priority_order: List[int] = field(default_factory=list)
    estimated_depth: int = 1


@dataclass
class ExecutionResult:
    """Result from Execute phase"""
    tool: ToolType
    query: str
    success: bool
    data: Any = None
    error: Optional[str] = None
    confidence: float = 0.0


@dataclass
class ReviewAssessment:
    """Assessment from Review phase"""
    objective_met: bool
    confidence_score: float
    gaps_identified: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class AdjustmentStrategy:
    """Strategy from Adjust phase"""
    continue_investigation: bool
    new_queries: List[str] = field(default_factory=list)
    tools_to_add: List[ToolType] = field(default_factory=list)
    max_cycles_reached: bool = False


class GuardrAgent:
    """
    Autonomous OSINT agent using deterministic PERA cycles

    Plan: Decompose investigation into structured queries
    Execute: Run tools in priority order
    Review: Validate results against objective
    Adjust: Refine strategy based on gaps
    """

    def __init__(self, config: Dict[str, Any], max_cycles: int = 3, use_openrouter: bool = True):
        self.config = config
        self.use_openrouter = use_openrouter

        if use_openrouter:
            from src.llm.openrouter_client import OpenRouterClient
            import os
            openrouter_key = os.getenv("OPEN_ROUTER_API_KEY")
            if not openrouter_key:
                raise ValueError("OPEN_ROUTER_API_KEY not set in environment")
            self.openrouter = OpenRouterClient(
                api_key=openrouter_key,
                default_model="openai/o3-mini"
            )
            logger.info("Using OpenRouter with o3-mini for high-reasoning planning")
        else:
            self.llm_client = LLMClient.from_config(config)

        self.max_cycles = max_cycles
        self.cycle_count = 0
        self.execution_history: List[Dict[str, Any]] = []

    def investigate(self, objective: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Run full PERA investigation cycle

        Args:
            objective: Investigation goal (e.g., "Verify identity of John Doe in Austin, TX")
            context: Additional context (location, username, etc.)

        Returns:
            Final investigation report
        """
        logger.info(f"Starting Guardr investigation: {objective}")

        context = context or {}
        findings = []

        while self.cycle_count < self.max_cycles:
            self.cycle_count += 1
            logger.info(f"=== PERA Cycle {self.cycle_count}/{self.max_cycles} ===")

            # PLAN
            plan = self._plan_phase(objective, context, findings)
            if not plan.sub_queries:
                logger.info("No further queries to execute")
                break

            # EXECUTE
            results = self._execute_phase(plan)
            findings.extend(results)

            # REVIEW
            assessment = self._review_phase(objective, findings)

            # ADJUST
            adjustment = self._adjust_phase(assessment, plan)

            # Record cycle
            self.execution_history.append({
                "cycle": self.cycle_count,
                "plan": plan,
                "results": results,
                "assessment": assessment,
                "adjustment": adjustment
            })

            # Check if done
            if not adjustment.continue_investigation:
                logger.info(f"Investigation complete (confidence: {assessment.confidence_score:.2f})")
                break

            if adjustment.max_cycles_reached:
                logger.info("Max cycles reached")
                break

            # Update context for next cycle
            context.update({
                "previous_findings": [f.query for f in findings],
                "gaps": assessment.gaps_identified
            })

        return self._generate_report(objective, findings, self.execution_history)

    def _plan_phase(self, objective: str, context: Dict[str, Any],
                    previous_findings: List[ExecutionResult]) -> InvestigationPlan:
        """
        PLAN: Decompose investigation into structured queries
        """
        logger.info("Phase 1: PLAN")

                # Simplified deterministic planning - decompose by context fields
        sub_queries = []
        tools_required = []

        if context.get("name"):
            sub_queries.append(f"Verify identity of {context['name']}")
            tools_required.append(ToolType.WEB_SEARCH)

        if context.get("username"):
            sub_queries.append(f"Search username: {context['username']}")
            tools_required.append(ToolType.SOCIAL_LOOKUP)

        if context.get("email"):
            sub_queries.append(f"Check breach data for: {context['email']}")
            tools_required.append(ToolType.BREACH_CHECK)

        # If no context, use objective directly
        if not sub_queries:
            sub_queries = [objective]
            tools_required = [ToolType.WEB_SEARCH]

        try:
            plan_data = {
                "sub_queries": sub_queries,
                "tools_required": [t.value for t in tools_required],
                "priority_order": list(range(1, len(sub_queries) + 1)),
                "estimated_depth": min(len(sub_queries), 2)
            }
            plan = InvestigationPlan(
                objective=objective,
                sub_queries=plan_data.get("sub_queries", []),
                tools_required=[ToolType(t) for t in plan_data.get("tools_required", [])],
                priority_order=plan_data.get("priority_order", []),
                estimated_depth=plan_data.get("estimated_depth", 1)
            )

            logger.info(f"Plan created: {len(plan.sub_queries)} queries, {len(plan.tools_required)} tools")
            return plan

        except Exception as e:
            logger.error(f"Plan phase failed: {e}")
            # Fallback basic plan
            return InvestigationPlan(
                objective=objective,
                sub_queries=[objective],
                tools_required=[ToolType.WEB_SEARCH],
                priority_order=[1],
                estimated_depth=1
            )

    def _execute_phase(self, plan: InvestigationPlan) -> List[ExecutionResult]:
        """
        EXECUTE: Run tools in priority order
        """
        logger.info("Phase 2: EXECUTE")

        results = []

        for idx, query in enumerate(plan.sub_queries):
            tool = plan.tools_required[idx] if idx < len(plan.tools_required) else ToolType.WEB_SEARCH
            priority = plan.priority_order[idx] if idx < len(plan.priority_order) else 999

            logger.info(f"Executing: {tool.value} for '{query}' (priority: {priority})")

            # Execute tool (placeholder - will implement actual tool calls)
            result = self._execute_tool(tool, query)
            results.append(result)

        return results

    def _execute_tool(self, tool: ToolType, query: str) -> ExecutionResult:
        """
        Execute a single OSINT tool
        """
        # Placeholder - integrate actual Kallisto tools
        from src.agents.web_agent import WebAgent

        try:
            if tool == ToolType.WEB_SEARCH:
                from src.modules.person_lookup import lookup_person

                # Use Kallisto's person_lookup for web investigation
                result = lookup_person(query, f"Investigate: {query}", self.config)

                return ExecutionResult(
                    tool=tool,
                    query=query,
                    success=True,
                    data=result,
                    confidence=0.7
                )
            else:
                # Other tools to be implemented
                return ExecutionResult(
                    tool=tool,
                    query=query,
                    success=False,
                    error=f"Tool {tool.value} not yet implemented"
                )

        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return ExecutionResult(
                tool=tool,
                query=query,
                success=False,
                error=str(e)
            )

    def _review_phase(self, objective: str, findings: List[ExecutionResult]) -> ReviewAssessment:
        """
        REVIEW: Validate results against objective
        """
        logger.info("Phase 3: REVIEW")

        findings_summary = [
            {
                "tool": f.tool.value,
                "query": f.query,
                "success": f.success,
                "confidence": f.confidence
            }
            for f in findings
        ]

        # Deterministic review logic
        successful_findings = [f for f in findings if f.success]
        total_confidence = sum(f.confidence for f in successful_findings) / len(findings) if findings else 0.0

        objective_met = len(successful_findings) >= 2 or total_confidence > 0.8

        gaps = []
        if not successful_findings:
            gaps.append("No successful investigations completed")
        elif len(successful_findings) < len(findings):
            gaps.append(f"{len(findings) - len(successful_findings)} investigations failed")

        try:
            assessment_data = {
                "objective_met": objective_met,
                "confidence_score": total_confidence,
                "gaps_identified": gaps,
                "recommendations": ["Continue investigation" if not objective_met else "Investigation complete"]
            }
            assessment = ReviewAssessment(
                objective_met=assessment_data.get("objective_met", False),
                confidence_score=assessment_data.get("confidence_score", 0.0),
                gaps_identified=assessment_data.get("gaps_identified", []),
                recommendations=assessment_data.get("recommendations", [])
            )

            logger.info(f"Review: objective_met={assessment.objective_met}, confidence={assessment.confidence_score:.2f}")
            return assessment

        except Exception as e:
            logger.error(f"Review phase failed: {e}")
            return ReviewAssessment(
                objective_met=False,
                confidence_score=0.0,
                gaps_identified=["Review phase failed"],
                recommendations=["Retry investigation"]
            )

    def _adjust_phase(self, assessment: ReviewAssessment, plan: InvestigationPlan) -> AdjustmentStrategy:
        """
        ADJUST: Refine strategy based on gaps
        """
        logger.info("Phase 4: ADJUST")

        # Deterministic adjustment logic
        continue_investigation = not assessment.objective_met and self.cycle_count < self.max_cycles
        max_cycles_reached = self.cycle_count >= self.max_cycles

        if assessment.objective_met or assessment.confidence_score > 0.8:
            logger.info("Objective satisfied, stopping investigation")
            return AdjustmentStrategy(
                continue_investigation=False,
                max_cycles_reached=False
            )

        if max_cycles_reached:
            logger.info("Max cycles reached")
            return AdjustmentStrategy(
                continue_investigation=False,
                max_cycles_reached=True
            )

        # Generate new queries from gaps
        new_queries = [f"Investigate: {gap}" for gap in assessment.gaps_identified[:3]]

        logger.info(f"Adjustment: continue={continue_investigation}, {len(new_queries)} new queries")

        return AdjustmentStrategy(
            continue_investigation=continue_investigation,
            new_queries=new_queries,
            tools_to_add=[ToolType.WEB_SEARCH],
            max_cycles_reached=False
        )

    def _generate_report(self, objective: str, findings: List[ExecutionResult],
                        history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate final investigation report
        """
        logger.info("Generating final report")

        successful_findings = [f for f in findings if f.success]

        report = {
            "objective": objective,
            "total_cycles": self.cycle_count,
            "total_findings": len(findings),
            "successful_findings": len(successful_findings),
            "final_confidence": history[-1]["assessment"].confidence_score if history else 0.0,
            "execution_history": history,
            "findings": [
                {
                    "tool": f.tool.value,
                    "query": f.query,
                    "success": f.success,
                    "confidence": f.confidence,
                    "data": str(f.data)[:500] if f.data else None
                }
                for f in findings
            ]
        }

        return report


def main():
    """Test Guardr agent"""
    config = load_config()

    agent = GuardrAgent(config, max_cycles=2)

    report = agent.investigate(
        objective="Verify the identity and online presence of John Doe",
        context={
            "name": "John Doe",
            "location": "Austin, TX",
            "age_range": "25-35"
        }
    )

    print("\n=== GUARDR INVESTIGATION REPORT ===")
    print(json.dumps(report, indent=2, default=str))


if __name__ == "__main__":
    main()
