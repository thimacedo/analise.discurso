import React, { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2, Clock, Zap, TrendingUp, BarChart3, RefreshCw } from 'lucide-react';

const WorkersMetricsDashboard = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/workers/dashboard');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching metrics:', err);
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, 10000); // Refresh every 10s
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getHealthColor = (status) => {
    switch(status) {
      case 'green': return '#10b981';
      case 'yellow': return '#f59e0b';
      case 'red': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getWorkerColor = (status) => {
    return status === 'healthy' ? '#10b981' : '#f59e0b';
  };

  if (loading && !metrics) {
    return (
      <div className="p-6 bg-gradient-to-br from-slate-900 to-slate-800 rounded-lg">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <RefreshCw className="animate-spin mx-auto mb-3" size={32} color="#06b6d4" />
            <p className="text-slate-300">Carregando métricas de workers...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-900/20 border border-red-500 rounded-lg">
        <div className="flex items-start gap-3">
          <AlertCircle size={24} className="text-red-400 flex-shrink-0" />
          <div>
            <h3 className="text-red-300 font-bold">Erro ao carregar métricas</h3>
            <p className="text-red-200 text-sm">{error}</p>
          </div>
        </div>
      </div>
    );
  }

  if (!metrics) return null;

  const {
    total_workers,
    healthy_workers,
    degraded_workers,
    system_health,
    total_executions,
    total_successful,
    overall_success_rate,
    total_items_processed,
    avg_system_throughput_items_per_sec,
    workers = []
  } = metrics;

  return (
    <div className="space-y-6 bg-gradient-to-br from-slate-950 to-slate-900 p-6 rounded-lg">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white flex items-center gap-2">
          <BarChart3 size={28} className="text-cyan-400" />
          Dashboard de Workers
        </h2>
        <button
          onClick={() => setAutoRefresh(!autoRefresh)}
          className={`px-3 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition ${
            autoRefresh 
              ? 'bg-cyan-600 text-white' 
              : 'bg-slate-700 text-slate-300'
          }`}
        >
          <RefreshCw size={16} />
          {autoRefresh ? 'Auto' : 'Manual'}
        </button>
      </div>

      {/* System Health Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Overall Health */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-3">
            <CheckCircle2 size={20} style={{ color: getHealthColor(system_health) }} />
            <span className="text-slate-400 text-sm">Saúde Geral</span>
          </div>
          <div className="text-3xl font-bold text-white capitalize">{system_health}</div>
          <p className="text-xs text-slate-500 mt-1">{healthy_workers}/{total_workers} saudáveis</p>
        </div>

        {/* Success Rate */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-3">
            <TrendingUp size={20} className="text-emerald-400" />
            <span className="text-slate-400 text-sm">Taxa de Sucesso</span>
          </div>
          <div className="text-3xl font-bold text-emerald-400">{overall_success_rate}%</div>
          <p className="text-xs text-slate-500 mt-1">{total_successful}/{total_executions} execuções</p>
        </div>

        {/* Throughput */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-3">
            <Zap size={20} className="text-yellow-400" />
            <span className="text-slate-400 text-sm">Throughput</span>
          </div>
          <div className="text-3xl font-bold text-yellow-400">{avg_system_throughput_items_per_sec}</div>
          <p className="text-xs text-slate-500 mt-1">itens/segundo</p>
        </div>

        {/* Total Items */}
        <div className="bg-slate-800 border border-slate-700 rounded-lg p-4">
          <div className="flex items-center gap-3 mb-3">
            <Clock size={20} className="text-blue-400" />
            <span className="text-slate-400 text-sm">Total Processado</span>
          </div>
          <div className="text-3xl font-bold text-blue-400">{total_items_processed.toLocaleString()}</div>
          <p className="text-xs text-slate-500 mt-1">itens no total</p>
        </div>
      </div>

      {/* Workers List */}
      <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
        <div className="p-4 border-b border-slate-700 bg-slate-900">
          <h3 className="text-lg font-bold text-white">Status dos Workers</h3>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-700/50 border-b border-slate-700">
              <tr>
                <th className="px-4 py-3 text-left text-slate-300">Worker</th>
                <th className="px-4 py-3 text-center text-slate-300">Status</th>
                <th className="px-4 py-3 text-right text-slate-300">Taxa Sucesso</th>
                <th className="px-4 py-3 text-right text-slate-300">Latência Média (ms)</th>
                <th className="px-4 py-3 text-right text-slate-300">Throughput</th>
                <th className="px-4 py-3 text-right text-slate-300">Últimas 5 Falhas</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700">
              {workers.length > 0 ? (
                workers.map((worker, idx) => (
                  <tr key={idx} className="hover:bg-slate-700/30 transition">
                    <td className="px-4 py-3">
                      <div>
                        <div className="font-semibold text-white">{worker.worker}</div>
                        <div className="text-xs text-slate-400">
                          {worker.total_executions} execuções
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span 
                        className="px-3 py-1 rounded-full text-xs font-bold text-white"
                        style={{ backgroundColor: getWorkerColor(worker.status) + '40', color: getWorkerColor(worker.status) }}
                      >
                        {worker.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-white">
                      {worker.success_rate}%
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-yellow-400">
                      {worker.avg_duration_ms}ms
                    </td>
                    <td className="px-4 py-3 text-right font-mono text-emerald-400">
                      {worker.avg_throughput_items_per_sec} items/s
                    </td>
                    <td className="px-4 py-3 text-right">
                      {worker.recent_errors.length > 0 ? (
                        <span className="text-red-400 font-bold">
                          {worker.recent_errors.length}
                        </span>
                      ) : (
                        <span className="text-slate-500">-</span>
                      )}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="6" className="px-4 py-8 text-center text-slate-400">
                    Nenhum worker com métricas registradas ainda
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Errors Alert */}
      {workers.some(w => w.recent_errors.length > 0) && (
        <div className="bg-red-900/20 border border-red-500/50 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <AlertCircle size={20} className="text-red-400 flex-shrink-0 mt-1" />
            <div>
              <h4 className="text-red-300 font-bold mb-2">Erros Recentes Detectados</h4>
              <div className="space-y-2">
                {workers
                  .filter(w => w.recent_errors.length > 0)
                  .map((worker, idx) => (
                    <div key={idx} className="text-sm text-red-200">
                      <span className="font-semibold">{worker.worker}:</span> {worker.recent_errors[0].error}
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Last Updated */}
      <div className="text-xs text-slate-500 text-right">
        Atualizado: {new Date(metrics.timestamp).toLocaleTimeString('pt-BR')}
      </div>
    </div>
  );
};

export default WorkersMetricsDashboard;
