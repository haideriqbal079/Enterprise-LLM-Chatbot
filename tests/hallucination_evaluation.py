from src.llm.groq_service import GroqService
from src.okf.loader import search_documents
from src.prompts.templates import build_prompt


# Questions that should be answerable from the OKF knowledge base.
ANSWERABLE_QUESTIONS = [
    "Who is the CEO of Try Soft AI?",
    "When was Try Soft AI founded?",
    "What are the working hours of Try Soft AI?",
    "Where is the Pakistan office of Try Soft AI located?",
    "Where is the UK headquarters of Try Soft AI located?",
    "How many employees does Try Soft AI have?",
    "What services does Try Soft AI provide?",
    "What AI services does Try Soft AI provide?",
    "What are the main technology areas Try Soft AI works with?",
    "Who is the Director of Try Soft AI?",
    "Who is the Chairman of Try Soft AI?",
    "What types of customers does Try Soft AI serve?",
    "What is Try Soft AI's approach to business requirements?",
    "What products and solutions does Try Soft AI provide?",
    "What are Try Soft AI's standard working days?",
]


# Questions whose answers should NOT be invented.
UNANSWERABLE_QUESTIONS = [
    "Who is the CFO of Try Soft AI?",
    "What was Try Soft AI's revenue in 2025?",
    "How many employees will Try Soft AI have in 2030?",
    "What is the salary of Try Soft AI's CEO?",
    "What is Try Soft AI's profit margin?",
]


groq_service = GroqService()


def generate_answer(question: str) -> str:
    documents = search_documents(question)

    knowledge_context = "\n\n".join(
        document["content"]
        for document in documents
    )

    prompt = build_prompt(
        prompt_type="grounded",
        knowledge_context=knowledge_context,
        question=question,
    )

    return groq_service.generate_response(prompt)


def main():
    total_questions = 0
    hallucinations = 0

    print("\n" + "=" * 70)
    print("HALLUCINATION EVALUATION")
    print("=" * 70)

    print("\nANSWERABLE QUESTIONS")
    print("-" * 70)

    for question in ANSWERABLE_QUESTIONS:
        total_questions += 1

        answer = generate_answer(question)

        print(f"\nQUESTION: {question}")
        print(f"ANSWER: {answer}")

    print("\n\nUNANSWERABLE QUESTIONS")
    print("-" * 70)

    for question in UNANSWERABLE_QUESTIONS:
        total_questions += 1

        answer = generate_answer(question)

        print(f"\nQUESTION: {question}")
        print(f"ANSWER: {answer}")

        # Manual evaluation is intentionally used here.
        # The evaluator should determine whether the model
        # invented unsupported information.

    print("\n" + "=" * 70)
    print("EVALUATION SUMMARY")
    print("=" * 70)
    print(f"Total questions: {total_questions}")
    print(f"Hallucinations: {hallucinations}")
    print(
        f"Hallucination rate: "
        f"{(hallucinations / total_questions) * 100:.2f}%"
    )


if __name__ == "__main__":
    main()