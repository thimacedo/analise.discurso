"""
PASA v17 - XP Engine: Motor de Recompensas e Gamificação
"""

# Constantes de Recompensa
XP_SUCCESS = 10
XP_CRITICAL_HIT = 25
XP_CLEAN_EXTRACTION = 5

# Penalidades
XP_PENALTY_TIMEOUT = -50
XP_PENALTY_AUTH_FAIL = -50
XP_PENALTY_HIGH_REJECTION = -20

# Limiares de Nível (Refletidos no Trigger SQL)
LEVEL_THRESHOLDS = {
    1: 0,     # Recruta
    2: 500,   # Sentinela
    3: 1500,  # Analista
    4: 3000,  # Caçador
    5: 6000   # Mestre Forense
}

def calculate_level(xp: int) -> int:
    """Calcula o nível com base no XP acumulado."""
    level = 1
    for lvl, threshold in sorted(LEVEL_THRESHOLDS.items(), reverse=True):
        if xp >= threshold:
            level = lvl
            break
    return level

def calculate_run_xp(success: bool, critical_hits: int = 0, rejections: int = 0, total_items: int = 0, auth_fail: bool = False, timeout: bool = False) -> int:
    """Calcula o XP líquido de uma execução de worker."""
    if timeout or auth_fail:
        return XP_PENALTY_AUTH_FAIL
    
    if not success:
        return 0
    
    xp = XP_SUCCESS
    xp += (critical_hits * XP_CRITICAL_HIT)
    
    # Bônus de extração limpa
    if total_items > 0 and rejections == 0:
        xp += XP_CLEAN_EXTRACTION
        
    # Penalidade por alta rejeição
    if total_items > 0 and (rejections / total_items) > 0.5:
        xp += XP_PENALTY_HIGH_REJECTION
        
    return xp
