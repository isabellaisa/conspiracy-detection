from enum import Enum
from dataclasses import dataclass

class PromptType(Enum):

    SIMPLE = "simple"
    DEFINITION = "defintion"


@dataclass(frozen=True)
class Prompt:

    prompt_type: PromptType
    prompt_body: str

    @property
    def type(self) -> PromptType:
        return self.prompt_type

    @property
    def promptBody(self) -> str:
        return self.prompt_body


    
SIMPLE_PROMPT = Prompt(
    PromptType.SIMPLE, 
    (
        "Decide whether the given video talks about "
        "a conspiracy theory or not (if yes output = 1/else output = 0)."
        "Provide just your output, no justification."
        )
    )

DEFINITION_PROMPT = Prompt(
    PromptType.DEFINITION,
    (
        "Given this definition of conspiracy theory:"
        "A conspiracy theory is a belief that two or more actors have coordinated in "
        "secret to achieve an outcome and that their conspiracy is of public interest but not public knowledge."
        " Conspiracy theories (a) are oppositional, which means they oppose publicly accepted understandings of events;"
        " (b) describe malevolent or forbidden acts; (c) ascribe agency to individuals and groups rather than to impersonal or systemic forces;"
        " (d) are epistemically risky, meaning that though they are not necessarily false or implausible,"
        " taken collectively they are more prone to falsity than other types of belief;"
        " and (e) are social constructs that are not merely adopted by individuals but are shared with social objectives in mind,"
        " and they have the potential not only to represent and interpret reality but also to fashion new social realities."
        "Decide whether the given video talks about "
        "a conspiracy theory or not (if yes output = 1/else output = 0)."
        "Provide just your output, no justification."
        )
) 

PROMPTS = [
    SIMPLE_PROMPT,
    DEFINITION_PROMPT
]

