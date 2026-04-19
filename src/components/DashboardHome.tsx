import React, { useMemo, useState } from 'react';
import { useAuthStore } from '../presentation/state/useAuthStore';
import { useProcessos } from '../presentation/hooks/useProcessos';
import { 
  Database, 
  ShieldCheck, 
  Bot, 
  Activity, 
  Terminal,
  Cpu,
  Zap,
  TrendingUp,
  AlertTriangle,
  History
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { useModal } from '../context/ModalContext';
import { aiService } from '../services/aiService';
import { supabase } from '../lib/supabase';

// 🧩 Atomic Industrial Primitives
const MetricSlot = ({ label, value, icon: Icon, color = "safety-orange" }: any) => (
  <div className="module-panel flex flex-col gap-4 group">
    <div className="flex justify-between items-start">
      <div className={`p-3 rounded-xl bg-chassis shadow-industrial-floating text-${color} transition-all group-hover:scale-110`}>
        <Icon size={20} />
      </div>
      <div className="h-6 w-1 rounded-full bg-recessed shadow-inner" />
    </div>
    <div>
      <span className="technical-label">{label}</span>
      <h3 className="text-3xl font-black font-mono mt-1 tracking-tighter tabular-nums">{value}</h3>
    </div>
  </div>
);

export default function DashboardHome() {
  const { currentUser } = useAuthStore();
  const { data: processos = [] } = useProcessos(currentUser?.organization_id);
  const { showModal } = useModal();
  const [diagStatus, setDiagStatus] = useState<any>(null);

  const runDiagnostic = async () => {
    setDiagStatus('running');
    const t0 = performance.now();
    try {
      const { error } = await supabase.from('perfis').select('id').limit(1);
      const latency = Math.round(performance.now() - t0);
      
      showModal("SYSTEM DIAGNOSTIC v5.6", (
        <div className="bg-black p-8 rounded-2xl font-mono text-emerald-500 screen-crt min-h-[400px]">
           <div className="flex justify-between items-center mb-6 border-b border-emerald-900/30 pb-4">
              <span className="text-[10px] font-black uppercase tracking-widest text-emerald-700">Audit Trace #772-B</span>
              <div className="led-indicator led-online h-3 w-3"></div>
           </div>
           <p className="mb-2 uppercase tracking-tighter text-xs">🚀 Initializing forensic scan...</p>
           <p className="mb-2 uppercase tracking-tighter text-xs">📡 Network Latency: <span className="text-white font-black">{latency}ms</span></p>
           <p className="mb-2 uppercase tracking-tighter text-xs">🗄️ Database Auth: <span className={error ? 'text-rose-500' : 'text-white'}>{error ? 'FAIL' : 'AUTHORIZED'}</span></p>
           <p className="mb-2 uppercase tracking-tighter text-xs">🤖 AI Logic Core: <span className="text-white">STANDBY_OK</span></p>
           <p className="mt-12 text-[10px] text-emerald-900 border-t border-emerald-900/20 pt-4 uppercase">© INOVASYS OPERATING SYSTEM - 2026</p>
        </div>
      ));
    } catch (e) {
      setDiagStatus('error');
    }
  };

  return (
    <div className="space-y-12 pb-24">
      {/* 🚀 Header Module */}
      <div className="flex flex-col xl:flex-row xl:items-end justify-between gap-8">
        <div>
           <span className="technical-label text-safety-orange flex items-center gap-2 mb-2">
             <Zap size={12} fill="currentColor" />
             Command Center Active
           </span>
           <h2 className="text-5xl font-black tracking-tighter">
             Dashboard <span className="text-recessed drop-shadow-[0_1px_0_#fff]">OSINT</span>
           </h2>
        </div>
        
        <div className="flex items-center gap-3 bg-recessed/20 p-2 rounded-2xl shadow-inner border border-white/40">
           <div className="flex flex-col items-end px-4">
              <span className="technical-label !text-[8px]">Session ID</span>
              <span className="font-mono font-bold text-xs uppercase tracking-tighter">{currentUser?.id?.substring(0, 12)}</span>
           </div>
           <button 
             onClick={runDiagnostic}
             className="key-primary !py-4 !px-8 h-14"
           >
             <Terminal size={18} />
             Run Master Diagnostic
           </button>
        </div>
      </div>

      {/* 🧩 Hardware Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
        <MetricSlot label="Total Collected" value={processos.length * 142} icon={Database} />
        <MetricSlot label="Critical Alerts" value="24" icon={AlertTriangle} color="rose-500" />
        <MetricSlot label="Processing Uptime" value="99.9%" icon={Activity} color="emerald-600" />
        <MetricSlot label="Active Nodes" value="135" icon={Cpu} color="ink" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
        {/* 📟 Main Telemetry Panel */}
        <div className="lg:col-span-2 module-panel-elevated !p-0">
           <div className="p-8 border-b border-recessed flex justify-between items-center bg-panel/30">
              <div className="flex items-center gap-3">
                 <History size={18} className="text-label" />
                 <h4 className="text-sm font-black tracking-widest">HOSTILITY TIMELINE</h4>
              </div>
              <div className="flex gap-1">
                 {[1,2,3].map(i => <div key={i} className="h-6 w-1 bg-recessed rounded-full" />)}
              </div>
           </div>
           <div className="p-10 h-80 bg-chassis/40">
              <div className="w-full h-full flex flex-col items-center justify-center border border-dashed border-recessed rounded-xl opacity-20">
                 <Activity size={48} />
                 <span className="technical-label mt-4">Telemetry Stream Waiting...</span>
              </div>
           </div>
        </div>

        {/* 🛠️ Maintenance & Health Panel */}
        <div className="module-panel bg-ink !text-chassis">
           <div className="flex items-center gap-3 mb-8 border-b border-white/5 pb-6">
              <ShieldCheck className="text-safety-orange" size={24} />
              <h4 className="text-sm font-black tracking-widest text-white">SYSTEM INTEGRITY</h4>
           </div>
           
           <div className="space-y-8">
              <div className="space-y-3">
                 <div className="flex justify-between items-center">
                    <span className="technical-label !text-white/40">Encryption (AES-256)</span>
                    <span className="text-[9px] font-black bg-emerald-500 text-white px-2 py-0.5 rounded">SECURE</span>
                 </div>
                 <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden shadow-inner">
                    <div className="h-full w-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.4)]" />
                 </div>
              </div>

              <div className="space-y-3">
                 <div className="flex justify-between items-center">
                    <span className="technical-label !text-white/40">Neural Engine Load</span>
                    <span className="text-[9px] font-black text-safety-orange">OPTIMIZED</span>
                 </div>
                 <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden shadow-inner">
                    <motion.div 
                      animate={{ width: ["20%", "45%", "35%"] }}
                      transition={{ duration: 5, repeat: Infinity }}
                      className="h-full bg-safety-orange shadow-[0_0_8px_rgba(255,71,87,0.4)]" 
                    />
                 </div>
              </div>

              <button className="w-full mt-8 py-5 bg-white/5 border border-white/10 rounded-2xl font-black text-[11px] uppercase tracking-[0.2em] text-white hover:bg-white/10 transition-all active:scale-95">
                 View Incident Logs
              </button>
           </div>
        </div>
      </div>
    </div>
  );
}
