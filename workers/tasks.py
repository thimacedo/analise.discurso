from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()

redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

app = Celery('tasks',
             broker=redis_url,
             backend=redis_url,
             include=['workers.tasks'])

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='America/Sao_Paulo',
    enable_utc=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=30,
    task_max_retries=3
)

@app.task(bind=True, name='coletar_perfil')
def task_coletar_perfil(self, username: str, posts_por_perfil: int = 2):
    from coletor import ColetorPublico
    coletor = ColetorPublico()
    
    try:
        comentarios = coletor.coletar_perfil(username, posts_por_perfil)
        
        for comentario in comentarios:
            task_processar_comentario.delay(comentario.to_dict())
            
        return f"Coletado {len(comentarios)} comentários de {username}"
    except Exception as exc:
        self.retry(exc=exc, countdown=60)

@app.task(name='processar_comentario')
def task_processar_comentario(comentario_dados: dict):
    from processador import ProcessadorCorpus
    proc = ProcessadorCorpus()
    
    comentario_dados['texto_limpo'] = proc.limpar_texto(comentario_dados['texto_bruto'])
    
    task_classificar_comentario.delay(comentario_dados)
    return True

@app.task(name='classificar_comentario')
def task_classificar_comentario(comentario_dados: dict):
    from classificador_bertimbau import ClassificadorBERTimbau
    classificador = ClassificadorBERTimbau()
    
    resultado = classificador.classificar(comentario_dados['texto_limpo'])
    
    comentario_dados.update(resultado)
    
    task_salvar_banco.delay(comentario_dados)
    return True

@app.task(name='salvar_banco')
def task_salvar_banco(comentario_dados: dict):
    from database.repository import DatabaseRepository
    db = DatabaseRepository()
    
    candidato = db.salvar_candidato(comentario_dados['candidato_username'], {})
    
    comentario = db.salvar_comentario(candidato.id, comentario_dados)
    
    if comentario:
        db.salvar_classificacao(comentario.id, comentario_dados)
    
    return True

if __name__ == '__main__':
    app.start()