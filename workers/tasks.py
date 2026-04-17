from celery import Celery
import os
import time
from dotenv import load_dotenv
import pandas as pd

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

@app.task(bind=True, name='coletar_perfil', max_retries=3)
def task_coletar_perfil(self, username: str, posts_por_perfil: int = 2, comentarios_por_post: int = 10):
    from coletor_apify import ColetorApify
    
    try:
        coletor = ColetorApify()
        # Coletar os posts
        posts = coletor.coletar_posts([username], posts_por_perfil)
        if not posts:
            return f"Nenhum post encontrado para {username}"
            
        # Coletar os comentários
        comentarios = coletor.coletar_comentarios(posts, comentarios_por_post)
        
        # Disparar uma task de processamento para cada comentário (pipeline em streaming)
        count = 0
        for comp in comentarios:
            task_processar_comentario.delay(comp)
            count += 1
            
        return f"Coletados {count} comentários de {username}"
    except Exception as exc:
        # Exponencial backoff: 60s, 120s, 240s
        retry_delay = 60 * (2 ** self.request.retries)
        print(f"⚠️ Erro ao coletar perfil {username}: {exc}. Tentando novamente em {retry_delay}s...")
        raise self.retry(exc=exc, countdown=retry_delay)

@app.task(bind=True, name='processar_comentario', max_retries=3)
def task_processar_comentario(self, comentario_dados: dict):
    from processador import ProcessadorCorpus
    try:
        proc = ProcessadorCorpus()
        
        texto_bruto = comentario_dados.get('texto', '')
        
        # Limpeza Forense Vichi
        texto_limpo = proc.limpar_texto_forense(texto_bruto)
        
        # Se for vazio após limpeza, descartamos
        if not texto_limpo or len(texto_limpo.strip()) < 3:
            return "Descartado por ser muito curto após limpeza"
            
        comentario_dados['texto_limpo'] = texto_limpo
        
        task_classificar_comentario.delay(comentario_dados)
        return "Comentário processado com sucesso"
    except Exception as exc:
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_delay)

@app.task(bind=True, name='classificar_comentario', max_retries=3)
def task_classificar_comentario(self, comentario_dados: dict):
    from classificador_bertimbau import ClassificadorBERTimbau
    try:
        classificador = ClassificadorBERTimbau()
        
        # Classificação local (GPU/CPU)
        resultado = classificador.classificar(comentario_dados['texto_limpo'])
        
        comentario_dados.update(resultado)
        
        task_salvar_banco.delay(comentario_dados)
        return "Comentário classificado com sucesso"
    except Exception as exc:
        retry_delay = 60 * (2 ** self.request.retries)
        raise self.retry(exc=exc, countdown=retry_delay)

@app.task(bind=True, name='salvar_banco', max_retries=5)
def task_salvar_banco(self, comentario_dados: dict):
    from database.repository import DatabaseRepository
    try:
        db = DatabaseRepository()
        
        # Garantir candidato (o username no coletor_apify é retornado como 'candidato')
        candidato_username = comentario_dados.get('candidato')
        candidato = db.salvar_candidato(candidato_username, {})
        
        # Estruturar os dados do comentário para o BD
        dados_comentario = {
            'id_externo': f"{candidato_username}_{comentario_dados.get('timestamp', time.time())}_{hash(comentario_dados.get('texto'))}",
            'post_id': comentario_dados.get('post_url', ''),
            'autor_username': comentario_dados.get('autor_username', 'anon'),
            'texto_bruto': comentario_dados.get('texto', ''),
            'texto_limpo': comentario_dados.get('texto_limpo', ''),
            'data_publicacao': comentario_dados.get('timestamp', None),
            'likes': comentario_dados.get('likes_comentario', 0)
        }
        
        comentario = db.salvar_comentario(candidato.id, dados_comentario)
        
        # Se foi salvo corretamente e retornou um ID válido, salva a classificação
        if comentario and hasattr(comentario, 'id'):
            dados_classificacao = {
                'categoria_odio': comentario_dados.get('categoria_odio'),
                'score': comentario_dados.get('score'),
                'confianca': comentario_dados.get('confianca'),
                'modelo_versao': comentario_dados.get('modelo_versao')
            }
            db.salvar_classificacao(comentario.id, dados_classificacao)
            return "Salvo no banco de dados com sucesso"
            
        return "Comentário ignorado (já existente ou erro ao salvar)"
    except Exception as exc:
        retry_delay = 10 * (2 ** self.request.retries)
        print(f"⚠️ Erro ao salvar comentário no banco: {exc}. Retrying...")
        raise self.retry(exc=exc, countdown=retry_delay)

if __name__ == '__main__':
    app.start()
