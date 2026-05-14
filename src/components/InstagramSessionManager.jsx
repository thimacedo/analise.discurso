import React, { useState, useEffect } from 'react';
import { Shield, Key, RefreshCw, CheckCircle2, AlertTriangle, Save } from 'lucide-react';

const InstagramSessionManager = () => {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({
    session_id: '',
    ds_user_id: '',
    csrf_token: '',
    profile_name: 'default'
  });
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    fetchStatus();
  }, []);

  const fetchStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/sessions/instagram/status');
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      console.error('Erro ao buscar status da sessão:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage({ type: '', text: '' });

    try {
      const response = await fetch('/api/v1/sessions/instagram/update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      const data = await response.json();
      if (response.ok) {
        setMessage({ type: 'success', text: 'Sessão atualizada com sucesso!' });
        fetchStatus();
      } else {
        throw new Error(data.detail || 'Falha ao atualizar');
      }
    } catch (err) {
      setMessage({ type: 'error', text: `Erro: ${err.message}` });
    } finally {
      setSaving(false);
    }
  };

  if (loading) return (
    <div className="flex justify-center p-8">
      <RefreshCw className="animate-spin text-cyan-400" size={32} />
    </div>
  );

  return (
    <div className="bg-slate-900 border border-slate-700 rounded-xl overflow-hidden max-w-2xl mx-auto shadow-2xl">
      <div className="bg-slate-800 p-4 border-b border-slate-700 flex items-center gap-3">
        <Shield className="text-cyan-400" size={24} />
        <h3 className="text-white font-bold text-lg">Gerenciador de Sessão Instagram</h3>
      </div>

      <div className="p-6 space-y-6">
        {/* Status atual */}
        <div className={`p-4 rounded-lg flex items-center justify-between ${
          status?.status === 'active' ? 'bg-emerald-500/10 border border-emerald-500/30' : 'bg-amber-500/10 border border-amber-500/30'
        }`}>
          <div className="flex items-center gap-3">
            {status?.status === 'active' ? (
              <CheckCircle2 className="text-emerald-400" size={20} />
            ) : (
              <AlertTriangle className="text-amber-400" size={20} />
            )}
            <div>
              <p className="text-slate-200 font-medium">
                {status?.status === 'active' ? 'Sessão Ativa' : 'Sessão Ausente ou Expirada'}
              </p>
              {status?.last_updated && (
                <p className="text-xs text-slate-400">Atualizado em: {new Date(status.last_updated).toLocaleString('pt-BR')}</p>
              )}
            </div>
          </div>
          <button onClick={fetchStatus} className="p-2 hover:bg-slate-700 rounded-full transition">
            <RefreshCw size={18} className="text-slate-400" />
          </button>
        </div>

        {/* Formulário de Atualização */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-400 mb-1">Session ID</label>
              <input
                type="password"
                required
                className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:ring-2 focus:ring-cyan-500 outline-none transition"
                placeholder="Insira o sessionid do cookie"
                value={formData.session_id}
                onChange={(e) => setFormData({...formData, session_id: e.target.value})}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">DS User ID</label>
                <input
                  type="text"
                  required
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:ring-2 focus:ring-cyan-500 outline-none transition"
                  placeholder="ID numérico"
                  value={formData.ds_user_id}
                  onChange={(e) => setFormData({...formData, ds_user_id: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-400 mb-1">CSRF Token</label>
                <input
                  type="text"
                  required
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg p-2.5 text-slate-200 focus:ring-2 focus:ring-cyan-500 outline-none transition"
                  placeholder="Token de segurança"
                  value={formData.csrf_token}
                  onChange={(e) => setFormData({...formData, csrf_token: e.target.value})}
                />
              </div>
            </div>
          </div>

          {message.text && (
            <div className={`p-3 rounded-lg text-sm ${
              message.type === 'success' ? 'bg-emerald-500/20 text-emerald-300' : 'bg-red-500/20 text-red-300'
            }`}>
              {message.text}
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="w-full bg-cyan-600 hover:bg-cyan-500 disabled:bg-slate-700 text-white font-bold py-3 rounded-lg flex items-center justify-center gap-2 transition"
          >
            {saving ? <RefreshCw className="animate-spin" size={20} /> : <Save size={20} />}
            {saving ? 'Salvando...' : 'Salvar Nova Sessão'}
          </button>
        </form>
        
        <div className="bg-slate-800/50 p-4 rounded-lg border border-slate-700">
          <h4 className="text-slate-300 text-xs font-bold uppercase mb-2 flex items-center gap-1">
            <Key size={12} /> Dica de Segurança
          </h4>
          <p className="text-slate-400 text-xs leading-relaxed">
            Nunca compartilhe esses tokens. Eles dão acesso total à conta configurada. 
            Use uma conta de "dummy" ou monitoramento dedicada para evitar bloqueios na sua conta principal.
          </p>
        </div>
      </div>
    </div>
  );
};

export default InstagramSessionManager;
