import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from core.pasa_auditor import PASAAuditor

# Teste de pipeline forense
if __name__ == "__main__":
    auditor = PASAAuditor()
    print(auditor.process("O perito encontrou uma prova forense."))
