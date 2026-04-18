import structlog
import os
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime

logger = structlog.get_logger()

class Monitoramento:
    def __init__(self):
        self.discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        self.metricas = {
            'coleta_sucesso': 0,
            'coleta_erro': 0,
            'classificacoes': 0,
            'classificacoes_neutro': 0,
            'inicio_execucao': datetime.utcnow()
        }
    
    def registrar_erro_coleta(self, perfil: str, erro: str):
        self.metricas['coleta_erro'] += 1
        logger.error("erro_coleta", perfil=perfil, erro=erro)
        
        taxa_erro = self._calcular_taxa_erro()
        if taxa_erro > 20:
            self._enviar_alerta(f"⚠️ ALERTA CRÍTICO: Taxa de erro da coleta atingiu {taxa_erro}%")
    
    def registrar_sucesso_coleta(self, perfil: str, quantidade: int):
        self.metricas['coleta_sucesso'] += 1
        logger.info("coleta_sucesso", perfil=perfil, quantidade=quantidade)
    
    def registrar_classificacao(self, categoria: str, confianca: float):
        self.metricas['classificacoes'] += 1
        if categoria == 'neutro':
            self.metricas['classificacoes_neutro'] += 1
        
        if self.metricas['classificacoes'] > 50:
            taxa_neutro = (self.metricas['classificacoes_neutro'] / self.metricas['classificacoes']) * 100
            if taxa_neutro > 95:
                self._enviar_alerta("⚠️ ALERTA: Modelo classificando 95% dos comentários como neutro. Provável falha no modelo.")
        
        # Active Learning: marcar comentários com baixa confiança
        if 0.45 < confianca < 0.85:
            logger.info("marcar_validacao_humana", confianca=confianca, categoria=categoria)
    
    def _calcular_taxa_erro(self):
        total = self.metricas['coleta_sucesso'] + self.metricas['coleta_erro']
        if total == 0:
            return 0
        return round((self.metricas['coleta_erro'] / total) * 100, 2)
    
    def _enviar_alerta(self, mensagem: str):
        logger.warning("alerta_disparado", mensagem=mensagem)
        
        if self.discord_webhook:
            try:
                webhook = DiscordWebhook(url=self.discord_webhook, content=mensagem)
                webhook.execute()
            except Exception as e:
                logger.error("falha_envio_alerta", erro=str(e))
    
    def resumo_execucao(self):
        tempo_execucao = (datetime.utcnow() - self.metricas['inicio_execucao']).total_seconds()
        logger.info("execucao_finalizada",
                    total_coletado=self.metricas['coleta_sucesso'],
                    total_erros=self.metricas['coleta_erro'],
                    taxa_erro=self._calcular_taxa_erro(),
                    tempo_segundos=round(tempo_execucao, 2))