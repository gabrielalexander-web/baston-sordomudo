"""Codificación Morse para el bastón.

Salida compatible con el firmware:
  '.' vibración corta, '-' vibración larga,
  '_' pausa entre elementos de una letra, '|' pausa entre letras.
Las palabras se separan con '||'.
"""
import unicodedata

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "Ñ": "--.--", "O": "---", "P": ".--.", "Q": "--.-",
    "R": ".-.", "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--",
    "X": "-..-", "Y": "-.--", "Z": "--..",
    "0": "-----", "1": ".----", "2": "..---", "3": "...--", "4": "....-",
    "5": ".....", "6": "-....", "7": "--...", "8": "---..", "9": "----.",
}


def normalize(text: str) -> str:
    """Mayúsculas y sin tildes, conservando la Ñ."""
    out = []
    for ch in text.upper():
        if ch == "Ñ":
            out.append(ch)
            continue
        decomposed = unicodedata.normalize("NFD", ch)
        out.append("".join(c for c in decomposed if unicodedata.category(c) != "Mn"))
    return "".join(out)


def text_to_pattern(text: str) -> str:
    words = []
    for word in normalize(text).split():
        letters = []
        for ch in word:
            code = MORSE.get(ch)
            if code:  # ignora caracteres sin código
                letters.append("_".join(code))
        if letters:
            words.append("|".join(letters))
    return "||".join(words)
