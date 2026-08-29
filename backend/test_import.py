import traceback
import sys
import warnings
warnings.filterwarnings("ignore")

try:
    from app.database import engine, Base
    with open("startup_error.txt", "w", encoding="utf-8") as f:
        f.write("Engine OK: " + str(engine.url) + "\n")
    print("Engine OK")
except Exception as e:
    with open("startup_error.txt", "w", encoding="utf-8") as f:
        traceback.print_exc(file=f)
    print("Engine FAILED - see startup_error.txt")
    sys.exit(1)

try:
    from app.models import User, ChatSession, Message, MoodLog
    with open("startup_error.txt", "a", encoding="utf-8") as f:
        f.write("Models OK\n")
    print("Models OK")
except Exception as e:
    with open("startup_error.txt", "a", encoding="utf-8") as f:
        traceback.print_exc(file=f)
    print("Models FAILED - see startup_error.txt")
    sys.exit(1)

print("All OK!")
