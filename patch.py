
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import sys
import subprocess
with open("scripts/work_session.py", "r", encoding="utf-8") as f:
    content = f.read()
content = content.replace("subprocess.Popen(", "subprocess.Popen( text=True, encoding='utf-8', errors='replace', ")
with open("scripts/work_session.py", "w", encoding="utf-8") as f:
    f.write(content)