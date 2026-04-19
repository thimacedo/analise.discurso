import React from 'react';
import { Menu, ChevronLeft, Power, Cpu, Shield, Search } from 'lucide-react';
import { motion } from 'motion/react';
import logoImg from '../../assets/logo-inovasys.png';

interface TopbarProps {
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
  camaraConfig: any;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
  session: any;
  userProfile: any;
  onSignOut: () => void;
  onSelectProcess: (id: string) => void;
}

export const Topbar: React.FC<TopbarProps> = ({
  isSidebarOpen,
  setIsSidebarOpen,
  onSignOut,
}) => {
  return (
    <header 
      className="sticky top-0 left-0 right-0 h-20 bg-chassis border-b border-recessed z-50 flex items-center justify-between px-6 shadow-md-1"
      style={{ backgroundImage: 'radial-gradient(circle at 20% 0%, rgba(255,255,255,0.4) 0%, transparent 40%)' }}
    >
      <div className="flex items-center gap-6">
        {/* Toggle Switch Lateral */}
        <button 
          onClick={() => setIsSidebarOpen(!isSidebarOpen)} 
          className="w-12 h-12 bg-chassis rounded-xl shadow-industrial-card flex items-center justify-center text-ink hover:text-safety-orange active:shadow-industrial-pressed transition-all"
          aria-label="Toggle Menu"
        >
          {isSidebarOpen ? <ChevronLeft size={22} /> : <Menu size={22} />}
        </button>
        
        <div className="flex items-center gap-4">
          <div className="p-2 bg-ink rounded-lg shadow-industrial-recessed">
            <img src={logoImg} className="h-6 w-auto brightness-0 invert opacity-90" alt="InovaSys" />
          </div>
          <div className="flex flex-col">
            <h1 className="text-sm font-black tracking-widest text-ink mb-0.5">FORENSIC ENGINE</h1>
            <div className="flex items-center gap-2">
              <div className="led-indicator led-online"></div>
              <span className="technical-label !text-[8px] text-emerald-600">Core System v5.6 Operational</span>
            </div>
          </div>
        </div>
      </div>

      {/* 🔍 Search Slot (Recessed) */}
      <div className="hidden md:flex flex-1 max-w-md mx-8 relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-label opacity-40" size={16} />
        <input 
          type="text" 
          placeholder="SEARCH EVIDENCE ID_..."
          className="data-slot w-full pl-12"
        />
      </div>
      
      <div className="flex items-center gap-4">
        {/* Hardware Info Slots */}
        <div className="hidden lg:flex items-center gap-6 px-6 py-2 bg-recessed/30 rounded-xl shadow-industrial-recessed border border-white/20">
           <div className="flex flex-col items-center gap-1">
             <span className="technical-label !text-[7px]">CPU LOAD</span>
             <div className="w-10 h-1 bg-ink/10 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: "20%" }} 
                  animate={{ width: ["20%", "45%", "15%"] }} 
                  transition={{ duration: 4, repeat: Infinity }}
                  className="h-full bg-emerald-500" 
                />
             </div>
           </div>
           <div className="flex flex-col items-center gap-1">
             <span className="technical-label !text-[7px]">MEM SQL</span>
             <div className="w-10 h-1 bg-ink/10 rounded-full overflow-hidden">
                <motion.div 
                  initial={{ width: "60%" }} 
                  animate={{ width: ["60%", "65%", "55%"] }} 
                  transition={{ duration: 3, repeat: Infinity }}
                  className="h-full bg-safety-orange" 
                />
             </div>
           </div>
        </div>

        {/* ⏻ Power Button */}
        <button 
          onClick={onSignOut}
          className="w-12 h-12 bg-chassis rounded-full shadow-industrial-card flex items-center justify-center text-label hover:text-safety-orange active:shadow-industrial-pressed group transition-all"
          title="TERMINATE SESSION"
        >
          <Power size={20} className="group-hover:drop-shadow-[0_0_8px_var(--color-safety-orange-glow)]" />
        </button>
      </div>
    </header>
  );
};
