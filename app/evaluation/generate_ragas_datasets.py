````python
import json
import time
import os
from typing import List, Dict, Any

from pydantic import BaseModel, ValidationError

from app.services.vector_service import VectorService
from app.services.llm_service import LLMService


# ============================================================
# 1. Configuration
# ============================================================

BATCH_SIZE = 15
QUESTIONS_PER_BATCH = 5

# Dataset جديد حتى لا نخلط النتائج القديمة بالجديدة
OUTPUT_FILE = "ragas_dataset_v2.json"

# إعدادات الحماية من Rate Limits
MAX_RETRIES = 3
DELAY_BETWEEN_BATCHES = 2
RETRY_DELAY = 10


# ============================================================
# 2. Pydantic Schemas
# ============================================================

class QAPair(BaseModel):
    question: str
    ground_truth: str

    # أرقام الـ chunks التي اعتمد عليها السؤال
    relevant_chunks: List[int]


# ============================================================
# 3. Helper Functions
# ============================================================

def clean_json_string(text: str) -> str:
    """
    إزالة Markdown code fences من استجابة الـ LLM
    """

    text = text.strip()

    if text.startswith("```json"):
        text = text[7:]

    elif text.startswith("```"):
        text = text[3:]

    if text.endswith("```"):
        text = text[:-3]

    return text.strip()


def load_existing_dataset() -> List[Dict[str, Any]]:
    """
    تحميل البيانات المحفوظة سابقاً لدعم Resume.
    """

    if not os.path.exists(OUTPUT_FILE):
        return []

    try:

        with open(
            OUTPUT_FILE,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

            if isinstance(data, list):
                return data

            print(
                "[!] Existing dataset is not a JSON list."
            )

            return []

    except Exception as e:

        print(
            f"[!] Warning: Could not load existing dataset: {e}"
        )

        return []


def save_dataset(
    dataset: List[Dict[str, Any]]
) -> None:
    """
    حفظ الـ dataset بعد كل batch.
    """

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            dataset,
            file,
            ensure_ascii=False,
            indent=4
        )


# ============================================================
# 4. Generate Q&A from One Batch
# ============================================================

def generate_qa(
    batch: List[Dict[str, Any]]
) -> str:

    context_parts = []

    for index, chunk in enumerate(
        batch,
        start=1
    ):

        text = chunk.get(
            "text",
            ""
        )

        page = chunk.get(
            "page",
            "unknown"
        )

        source = chunk.get(
            "source",
            "unknown"
        )

        context_parts.append(

            f"--- CHUNK {index} ---\n"
            f"Page: {page}\n"
            f"Source: {source}\n\n"
            f"{text}\n"

        )

    context = "\n".join(
        context_parts
    )

    prompt = f"""
You are generating a high-quality question-answer dataset
for evaluating a Retrieval-Augmented Generation (RAG) system.

You must use ONLY the tender context provided below.

Generate exactly {QUESTIONS_PER_BATCH}
question-answer pairs.

IMPORTANT RULES:

1. Every question MUST be answerable strictly from the provided context.

2. Do NOT use external knowledge.

3. Do NOT invent facts.

4. Questions should test useful tender information.

5. Prefer questions involving:
   - dates
   - numbers
   - financial conditions
   - eligibility requirements
   - technical requirements
   - scope of work
   - submission requirements
   - contract requirements
   - warranties
   - obligations
   - penalties
   - evaluation criteria
   - cybersecurity
   - compliance
   when these topics exist in the context.

6. Answers must be concise and directly supported by the context.

7. For EVERY question, identify the exact CHUNK number(s)
   that contain the information required to answer it.

8. The chunk numbers MUST correspond to the
   CHUNK numbers shown in the context.

9. Do NOT select unrelated chunks.

10. Use the minimum number of relevant chunks necessary.

11. If the answer requires information from multiple chunks,
    include all required chunk numbers.

12. Return ONLY valid JSON.

13. Do NOT return Markdown.

14. Do NOT return explanations before or after the JSON.

Required JSON format:

[
    {{
        "question": "Question here",
        "ground_truth": "Answer here",
        "relevant_chunks": [1]
    }},
    {{
        "question": "Question here",
        "ground_truth": "Answer here",
        "relevant_chunks": [3, 4]
    }}
]

Tender Context:

{context}
"""

    response = LLMService.generate(
        prompt=prompt,
        task_type="analysis",
        temperature=0.1
    )

    return response


# ============================================================
# 5. Parse and Validate Q&A
# ============================================================

def parse_qa(
    response: str,
    batch: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:

    try:

        # ----------------------------------------------------
        # Clean LLM response
        # ----------------------------------------------------

        cleaned_response = clean_json_string(
            response
        )

        data = json.loads(
            cleaned_response
        )

        if not isinstance(
            data,
            list
        ):

            print(
                "[!] LLM response is not a JSON list."
            )

            return []

        valid_data = []

        # ----------------------------------------------------
        # Validate every generated Q&A
        # ----------------------------------------------------

        for item in data:

            try:

                qa = QAPair.model_validate(
                    item
                )

            except ValidationError as e:

                print(
                    "\n[!] Invalid Q&A skipped:"
                )

                print(e)

                continue

            # ------------------------------------------------
            # Validate relevant chunk numbers
            # ------------------------------------------------

            relevant_chunk_numbers = []

            for chunk_number in qa.relevant_chunks:

                # يجب أن يكون رقم chunk صحيح
                if not isinstance(
                    chunk_number,
                    int
                ):

                    continue

                # يجب أن يكون داخل الـ batch
                if (
                    1
                    <= chunk_number
                    <= len(batch)
                ):

                    relevant_chunk_numbers.append(
                        chunk_number
                    )

            # إزالة التكرار مع الحفاظ على الترتيب
            relevant_chunk_numbers = list(
                dict.fromkeys(
                    relevant_chunk_numbers
                )
            )

            # لو مفيش chunks صحيحة
            if not relevant_chunk_numbers:

                print(
                    "[!] Q&A skipped because no valid "
                    "relevant chunks were provided."
                )

                print(
                    f"Question: {qa.question}"
                )

                continue

            # ------------------------------------------------
            # Build Ground Truth Contexts
            # ------------------------------------------------

            relevant_contexts = []

            metadata = []

            for chunk_number in relevant_chunk_numbers:

                # CHUNK 1 -> index 0
                chunk_index = (
                    chunk_number - 1
                )

                chunk = batch[
                    chunk_index
                ]

                text = chunk.get(
                    "text",
                    ""
                )

                if text:

                    relevant_contexts.append(
                        text
                    )

                metadata.append(
                    {
                        "source": chunk.get(
                            "source"
                        ),
                        "page": chunk.get(
                            "page"
                        ),
                        "tender_id": chunk.get(
                            "tender_id"
                        ),
                        "chunk_index": chunk_number
                    }
                )

            # ------------------------------------------------
            # Final Dataset Record
            # ------------------------------------------------

            valid_data.append(
                {
                    "question": qa.question.strip(),

                    "ground_truth": qa.ground_truth.strip(),

                    "ground_truth_contexts":
                        relevant_contexts,

                    "metadata":
                        metadata
                }
            )

        return valid_data

    # ========================================================
    # JSON Error
    # ========================================================

    except json.JSONDecodeError as e:

        print(
            "\n[!] Invalid JSON returned by LLM:"
        )

        print(e)

        print(
            "\nRaw response preview:"
        )

        print(
            response[:500]
        )

        return []

    # ========================================================
    # Unexpected Error
    # ========================================================

    except Exception as e:

        print(
            f"\n[!] Unexpected parsing error: {e}"
        )

        return []


# ============================================================
# 6. Main Dataset Generation Pipeline
# ============================================================

def generate_dataset(
    collection_name: str
) -> None:

    print(
        "=" * 60
    )

    print(
        "RAGAS DATASET GENERATOR V2"
    )

    print(
        "=" * 60
    )

    print(
        f"\nCollection: {collection_name}"
    )

    print(
        "\nLoading chunks from Qdrant..."
    )

    # --------------------------------------------------------
    # Load chunks
    # --------------------------------------------------------

    chunks = VectorService.get_all_chunks(
        collection_name=collection_name
    )

    print(
        f"Found {len(chunks)} chunks."
    )

    if not chunks:

        print(
            "[X] No chunks found. Process aborted."
        )

        return

    # --------------------------------------------------------
    # Load existing dataset
    # --------------------------------------------------------

    dataset = load_existing_dataset()

    print(
        f"Loaded {len(dataset)} existing "
        f"Q&A pairs from {OUTPUT_FILE}."
    )

    # --------------------------------------------------------
    # Calculate batches
    # --------------------------------------------------------

    total_batches = (
        len(chunks)
        + BATCH_SIZE
        - 1
    ) // BATCH_SIZE

    print(
        f"Total batches: {total_batches}"
    )

    # --------------------------------------------------------
    # Process batches
    # --------------------------------------------------------

    for batch_number, start in enumerate(
        range(
            0,
            len(chunks),
            BATCH_SIZE
        ),
        start=1
    ):

        batch = chunks[
            start:start + BATCH_SIZE
        ]

        print(
            f"\nProcessing batch "
            f"{batch_number}/{total_batches}..."
        )

        print(
            f"Batch contains {len(batch)} chunks."
        )

        response = None

        # ====================================================
        # Retry Logic
        # ====================================================

        for attempt in range(
            1,
            MAX_RETRIES + 1
        ):

            try:

                response = generate_qa(
                    batch
                )

                break

            except Exception as e:

                print(
                    f"[!] Exception on attempt "
                    f"{attempt}/{MAX_RETRIES}: {e}"
                )

                if attempt < MAX_RETRIES:

                    sleep_time = (
                        RETRY_DELAY
                        * attempt
                    )

                    print(
                        f"[*] Waiting "
                        f"{sleep_time} seconds "
                        f"before retry..."
                    )

                    time.sleep(
                        sleep_time
                    )

                else:

                    print(
                        f"[X] Batch "
                        f"{batch_number} failed "
                        f"after "
                        f"{MAX_RETRIES} attempts."
                    )

                    print(
                        "[*] Skipping to next batch."
                    )

        # ----------------------------------------------------
        # No response
        # ----------------------------------------------------

        if not response:

            continue

        # ====================================================
        # Parse generated Q&A
        # ====================================================

        qa_pairs = parse_qa(
            response,
            batch
        )

        if not qa_pairs:

            print(
                "[!] No valid Q&A generated "
                "for this batch."
            )

            continue

        # ====================================================
        # Add to dataset
        # ====================================================

        print(
            f"Successfully generated "
            f"{len(qa_pairs)} valid Q&A pair(s)."
        )

        dataset.extend(
            qa_pairs
        )

        # ====================================================
        # Save progress
        # ====================================================

        save_dataset(
            dataset
        )

        print(
            f"[+] Progress saved."
        )

        print(
            f"[+] Total Q&A pairs stored: "
            f"{len(dataset)}"
        )

        # ====================================================
        # Delay between batches
        # ====================================================

        if batch_number < total_batches:

            print(
                f"[*] Waiting "
                f"{DELAY_BETWEEN_BATCHES} seconds..."
            )

            time.sleep(
                DELAY_BETWEEN_BATCHES
            )

    # ========================================================
    # Finished
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "Dataset generation process finished!"
    )

    print(
        f"Total valid questions saved: "
        f"{len(dataset)}"
    )

    print(
        f"Saved to: {OUTPUT_FILE}"
    )

    print(
        "=" * 60
    )


# ============================================================
# 7. Entry Point
# ============================================================

if __name__ == "__main__":

    collection_name = input(
        "Enter collection name: "
    ).strip()

    if not collection_name:

        raise ValueError(
            "Collection name is required."
        )

    generate_dataset(
        collection_name
    )
````
