# Prompt Engineering Evaluation

## Prompt Variations

### 1. Concise
Designed to produce short, direct answers while remaining grounded in company knowledge.

### 2. Grounded
Designed to minimize hallucinations by explicitly prohibiting assumptions and outside knowledge.

### 3. Structured
Designed to organize answers using headings and bullet points.

## Test Questions

1. Who is the CEO of Try Soft AI?
2. When was Try Soft AI founded?
3. What are the working hours of Try Soft AI?
4. What services does Try Soft AI provide?
5. Who is the CFO of Try Soft AI?

## Evaluation Criteria

- Factual correctness
- Grounding in company knowledge
- Conciseness
- Response structure
- Handling of unavailable information

## Initial Result

All three prompt variations correctly answered the factual questions tested.

All three prompt variations correctly refused to provide unsupported information for the CFO question.

The Grounded prompt provided the best balance between factual grounding and response length.

The Structured prompt produced more detailed responses than necessary for simple questions.

The Concise prompt produced short and accurate responses but provides fewer explicit safeguards against assumptions.

## Selected Production Prompt

The Grounded prompt is selected as the initial production prompt because it provides the strongest explicit safeguards against hallucination while maintaining concise responses.