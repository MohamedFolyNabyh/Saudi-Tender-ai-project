from app.services.llm_service import LLMService


class SupervisorAgent:

    @classmethod
    def run(cls, state):

        question = state["question"]

        prompt = f"""
You are a routing supervisor for a Saudi Tender Management system.

Classify the user question into EXACTLY ONE of these intents:

sql
rag
report
risk
compare

RULES:

SQL:
Use sql ONLY when the question asks about data stored in the application database.

Examples:
- how many tenders
- how many tender
- number of tenders
- count tenders
- tender count
- how many projects
- number of projects
- count projects
- list all tenders
- list all projects
- show all tenders
- show all projects
- tender statuses
- how many users

RAG:
Use rag when asking about information inside the tender PDF/document.

Examples:
- what is the tender number?
- what is this tender about?
- what are the requirements?
- what are the penalties?
- what is the deadline?
- what are the technical specifications?

REPORT:
Use report when the user asks to generate a report or summary.

RISK:
Use risk when the user asks for risk analysis.

COMPARE:
Use compare when comparing two tenders.

VERY IMPORTANT:

"how many tender" = sql
"how many tenders" = sql
"tender count" = sql
"number of tenders" = sql
"how many projects" = sql

Return ONLY one word:

sql
rag
report
risk
compare

User question:
{question}

Intent:
"""

        # =====================================
        # Call LLM
        # =====================================

        result = LLMService.generate(prompt)

        # =====================================
        # Clean result
        # =====================================

        raw_result = result

        result = result.strip().lower()

        # =====================================
        # Extract intent
        # =====================================

        if result == "sql":
            intent = "sql"

        elif result == "rag":
            intent = "rag"

        elif result == "report":
            intent = "report"

        elif result == "risk":
            intent = "risk"

        elif result == "compare":
            intent = "compare"

        else:
            # Try to find intent inside LLM response
            if "sql" in result:
                intent = "sql"

            elif "rag" in result:
                intent = "rag"

            elif "report" in result:
                intent = "report"

            elif "risk" in result:
                intent = "risk"

            elif "compare" in result:
                intent = "compare"

            else:
                intent = "rag"

        # =====================================
        # Save intent
        # =====================================

        state["intent"] = intent

        # =====================================
        # DEBUG
        # =====================================

        print(
            "\n========== SUPERVISOR ==========",
            flush=True
        )

        print(
            f"QUESTION: {question}",
            flush=True
        )

        print(
            f"LLM RAW RESULT: {raw_result}",
            flush=True
        )

        print(
            f"CLEANED RESULT: {result}",
            flush=True
        )

        print(
            f"FINAL INTENT: {intent}",
            flush=True
        )

        print(
            "================================\n",
            flush=True
        )

        return state