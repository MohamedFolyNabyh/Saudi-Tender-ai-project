import json
import os
from pathlib import Path
from typing import Any, Dict, List

from ragas import evaluate
from ragas.dataset_schema import EvaluationDataset, SingleTurnSample
from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

from app.database.models.tender import Tender
from app.database.session import SessionLocal
from app.services.rag_service import RAGService

# ============================================================
# Configuration
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATASET_FILE = str(BASE_DIR / "ragas_dataset_v2.json")
OUTPUT_FILE = str(BASE_DIR / "ragas_results.json")

# عدد الأسئلة التي سيتم تقييمها
# ابدأ بـ 5 للتجربة، وبعد التأكد غيّرها إلى None
MAX_QUESTIONS = 10


# ============================================================
# Load Dataset
# ============================================================

def load_dataset() -> List[Dict[str, Any]]:
    """Load generated RAGAS dataset."""
    if not os.path.exists(DATASET_FILE):
        raise FileNotFoundError(f"Dataset not found: {DATASET_FILE}")

    with open(DATASET_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("Dataset must be a JSON list.")

    return data


# ============================================================
# Get Tender
# ============================================================

def get_tender(db: Any, tender_id: int) -> Tender:
    """Get Tender from database."""
    return db.query(Tender).filter(Tender.id == tender_id).first()


# ============================================================
# Run RAG
# ============================================================

def run_rag(tender: Tender, question: str) -> Dict[str, Any]:
    """Run RAG only once.

    IMPORTANT:
    We do NOT call RAGService.retrieve() after RAGService.ask().
    This prevents running the CrossEncoder twice for every question.
    """
    # --------------------------------------------------------
    # Run complete RAG pipeline
    # --------------------------------------------------------
    result = RAGService.ask(tender=tender, question=question)

    # --------------------------------------------------------
    # Extract answer
    # --------------------------------------------------------
    answer = result.get("answer", "")

    # --------------------------------------------------------
    # Try to get retrieved chunks from result
    # --------------------------------------------------------
    chunks = result.get("chunks", [])

    # --------------------------------------------------------
    # Alternative possible names
    # --------------------------------------------------------
    if not chunks:
        chunks = result.get("sources", [])

    # --------------------------------------------------------
    # Extract contexts
    # --------------------------------------------------------
    contexts = []
    for chunk in chunks:
        if isinstance(chunk, dict):
            text = chunk.get("text", "")
        else:
            text = str(chunk)

        if text:
            contexts.append(text)

    return {"answer": answer, "contexts": contexts}


# ============================================================
# Build RAGAS Dataset
# ============================================================

def build_evaluation_dataset(
    data: List[Dict[str, Any]], db: Any
) -> EvaluationDataset:
    samples = []

    # --------------------------------------------------------
    # Limit questions for testing
    # --------------------------------------------------------
    if MAX_QUESTIONS is not None:
        evaluation_data = data[:MAX_QUESTIONS]
    else:
        evaluation_data = data

    print(f"\nEvaluating {len(evaluation_data)} questions.")

    # ========================================================
    # Process Questions
    # ========================================================
    for index, item in enumerate(evaluation_data, start=1):
        # ----------------------------------------------------
        # Read dataset fields
        # ----------------------------------------------------
        question = item.get("question")
        ground_truth = item.get("ground_truth")
        ground_truth_contexts = item.get("ground_truth_contexts", [])
        metadata = item.get("metadata", [])

        # ----------------------------------------------------
        # Validate question
        # ----------------------------------------------------
        if not question:
            print(f"[!] Question {index} has no question field.")
            continue

        # ----------------------------------------------------
        # Validate ground truth
        # ----------------------------------------------------
        if not ground_truth:
            print(f"[!] Question {index} has no ground_truth field.")
            continue

        # ----------------------------------------------------
        # Validate metadata
        # ----------------------------------------------------
        if not metadata:
            print(f"[!] Question {index} has no metadata.")
            continue

        # ----------------------------------------------------
        # Get tender ID
        # ----------------------------------------------------
        tender_id = metadata[0].get("tender_id")
        if tender_id is None:
            print(f"[!] Question {index} has no tender_id.")
            continue

        # ----------------------------------------------------
        # Get Tender from DB
        # ----------------------------------------------------
        tender = get_tender(db, tender_id)
        if tender is None:
            print(f"[!] Tender {tender_id} not found.")
            continue

        # ====================================================
        # Run RAG
        # ====================================================
        print("\n" + "-" * 60)
        print(f"Evaluating {index}/{len(evaluation_data)}")
        print(f"Question: {question}")
        print(f"Tender ID: {tender_id}")

        try:
            rag_result = run_rag(tender=tender, question=question)
        except Exception as e:
            print(f"[X] RAG failed for question {index}:")
            print(e)
            continue

        # ----------------------------------------------------
        # Retrieved contexts & answer
        # ----------------------------------------------------
        retrieved_contexts = rag_result.get("contexts", [])
        answer = rag_result.get("answer", "")

        if not answer:
            print("[!] RAG returned empty answer.")

        # ----------------------------------------------------
        # Print retrieval information
        # ----------------------------------------------------
        print(f"Retrieved contexts: {len(retrieved_contexts)}")
        print(f"Ground-truth contexts: {len(ground_truth_contexts)}")

        # ====================================================
        # Create RAGAS Sample
        # ====================================================
        sample = SingleTurnSample(
            user_input=question,
            retrieved_contexts=retrieved_contexts,
            response=answer,
            reference=ground_truth,
        )
        samples.append(sample)

    # ========================================================
    # Return Dataset
    # ========================================================
    print("\n" + "=" * 60)
    print(f"Valid evaluation samples: {len(samples)}")
    print("=" * 60)

    return EvaluationDataset(samples=samples)


# ============================================================
# Run RAGAS
# ============================================================

def evaluate_rag(dataset: EvaluationDataset) -> Any:
    metrics = [
        Faithfulness(),
        ContextPrecision(),
        ContextRecall(),
        AnswerRelevancy(),
    ]

    print("\n" + "=" * 60)
    print("RUNNING RAGAS EVALUATION")
    print("=" * 60)

    result = evaluate(dataset=dataset, metrics=metrics)
    return result


# ============================================================
# Save Results
# ============================================================

def save_results(result: Any) -> None:
    result_df = result.to_pandas()
    result_df.to_json(
        OUTPUT_FILE, orient="records", force_ascii=False, indent=4
    )

    print(f"\nResults saved to:\n{OUTPUT_FILE}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    print("=" * 60)
    print("RAGAS RAG EVALUATION")
    print("=" * 60)

    # --------------------------------------------------------
    # Load dataset
    # --------------------------------------------------------
    print("\nLoading dataset...")
    data = load_dataset()
    print(f"Questions loaded: {len(data)}")

    if not data:
        print("Dataset is empty.")
        return

    # --------------------------------------------------------
    # Database
    # --------------------------------------------------------
    db = SessionLocal()

    try:
        # ----------------------------------------------------
        # Build evaluation dataset
        # ----------------------------------------------------
        evaluation_dataset = build_evaluation_dataset(data, db)

        if not evaluation_dataset.samples:
            print("\nNo valid evaluation samples found.")
            return

        # ----------------------------------------------------
        # Run RAGAS
        # ----------------------------------------------------
        result = evaluate_rag(evaluation_dataset)

        # ----------------------------------------------------
        # Print & Save results
        # ----------------------------------------------------
        print("\n" + "=" * 60)
        print("RAGAS RESULTS")
        print("=" * 60)
        print(result)

        save_results(result)

    finally:
        db.close()


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()