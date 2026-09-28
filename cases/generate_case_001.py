"""Generate the three offline demo cases."""

from pathlib import Path

from oiled.pipeline import generate_all_cases


def generate_case_001():
    generate_all_cases(Path(__file__).resolve().parent)


if __name__ == "__main__":
    generate_case_001()
