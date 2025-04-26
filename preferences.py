from typing import Callable, TypeVar

T = TypeVar('T')

class Preferences:
    def ask(self, question: str, qType: Callable[[str], T]) -> T:
        x = input(question)

        try:
            converted_value = qType(x)  # Convert input to the expected type
            return converted_value
        except ValueError:
            log(f"Invalid input. Could not convert to {qType.__name__}. Try again.")
            return self.ask(question, qType)