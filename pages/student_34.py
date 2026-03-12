import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from quiz_data import show_student_quiz, hide_sidebar

hide_sidebar()
show_student_quiz("34")
