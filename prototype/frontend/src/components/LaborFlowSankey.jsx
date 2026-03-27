import React from 'react';
import { motion } from 'framer-motion';
import { Network, ArrowRight } from 'lucide-react';

const LaborFlowSankey = ({ gapData }) => {
  const sector = gapData?.sector_context || 'General';
  // Use actual displacement rate from dataset, fallback to 35%
  const transitionRate = gapData?.sector_displacement_rate || 35.0;
  const augmentedRate = 100 - transitionRate;

  // Empirical flow for the sector
  const flows = [
    { from: "High-Risk Roles", to: "AI-Augmented", value: augmentedRate, color: "from-rose-500/40 to-cyan-500/40" },
    { from: "High-Risk Roles", to: "Structural Transition", value: transitionRate, color: "from-rose-500/40 to-slate-500/40" },
    { from: "Strategic Nodes", to: "AI-Augmented", value: 90, color: "from-emerald-500/40 to-cyan-500/40" },
    { from: "Strategic Nodes", to: "Structural Transition", value: 10, color: "from-emerald-500/40 to-slate-500/40" },
  ];

  return (
    <div className="bg-slate-900/40 p-10 rounded-3xl border border-white/5 shadow-2xl backdrop-blur-3xl h-[500px] flex flex-col">
      <div className="flex justify-between items-center mb-10">
        <div>
           <h3 className="text-sm font-black text-white uppercase tracking-[0.2em] flex items-center gap-3">
             <Network size={20} className="text-cyan-400" />
             Labor Reallocation Flow
           </h3>
           <p className="text-[10px] text-slate-500 font-mono mt-1 uppercase tracking-widest">Sector Projection: {sector || 'General'}</p>
        </div>
        <div className="text-[10px] bg-white/5 border border-white/10 px-3 py-1.5 rounded-full text-slate-400 font-bold uppercase tracking-widest">
            2026-2030 Horizon
        </div>
      </div>

      <div className="flex-1 relative">
         {/* Vertical Nodes - Left */}
         <div className="absolute left-0 top-0 bottom-0 w-32 flex flex-col justify-between py-10 z-10">
            <div className="p-4 bg-slate-900 border border-rose-500/30 rounded-2xl shadow-[0_0_20px_rgba(244,63,94,0.1)]">
                <div className="text-[10px] font-black text-rose-400 uppercase mb-1">High-Risk</div>
                <div className="text-[8px] text-slate-500 font-bold leading-tight">Legacy Process Focus</div>
            </div>
            <div className="p-4 bg-slate-900 border border-emerald-500/30 rounded-2xl shadow-[0_0_20px_rgba(16,185,129,0.1)]">
                <div className="text-[10px] font-black text-emerald-400 uppercase mb-1">Strategic</div>
                <div className="text-[8px] text-slate-500 font-bold leading-tight">Orchestration Focus</div>
            </div>
         </div>

         {/* Vertical Nodes - Right */}
         <div className="absolute right-0 top-0 bottom-0 w-32 flex flex-col justify-between py-10 z-10">
            <div className="p-4 bg-slate-900 border border-cyan-500/30 rounded-2xl shadow-[0_0_20px_rgba(6,182,212,0.1)]">
                <div className="text-[10px] font-black text-cyan-400 uppercase mb-1">Augmented</div>
                <div className="text-[8px] text-slate-500 font-bold leading-tight">AI-Human Synergy</div>
            </div>
            <div className="p-4 bg-slate-900 border border-slate-700/30 rounded-2xl shadow-xl">
                <div className="text-[10px] font-black text-slate-400 uppercase mb-1">Transition</div>
                <div className="text-[8px] text-slate-500 font-bold leading-tight">Sector Migration</div>
            </div>
         </div>

         {/* Interactive Flow Paths */}
         <svg className="w-full h-full absolute top-0 left-0 px-32 pointer-events-none">
            <defs>
               <linearGradient id="flow1" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.4" />
                  <stop offset="100%" stopColor="#06b6d2" stopOpacity="0.4" />
               </linearGradient>
               <linearGradient id="flow2" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#f43f5e" stopOpacity="0.2" />
                  <stop offset="100%" stopColor="#475569" stopOpacity="0.2" />
               </linearGradient>
            </defs>
            
            {/* Simple representation of flows */}
            <motion.path 
                d="M 10 70 Q 150 70, 300 70" 
                stroke="url(#flow1)" strokeWidth={Math.max(10, augmentedRate * 0.6)} fill="none"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 1.5, ease: "easeInOut" }}
            />
            <motion.path 
                d="M 10 80 Q 150 200, 300 300" 
                stroke="url(#flow2)" strokeWidth={Math.max(10, transitionRate * 0.6)} fill="none"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 1.5, delay: 0.2, ease: "easeInOut" }}
            />
            <motion.path 
                d="M 10 300 Q 150 200, 300 80" 
                stroke="#10b98144" strokeWidth="45" fill="none"
                initial={{ pathLength: 0, opacity: 0 }}
                animate={{ pathLength: 1, opacity: 1 }}
                transition={{ duration: 1.5, delay: 0.4, ease: "easeInOut" }}
            />
         </svg>
      </div>

      <div className="mt-8 p-6 bg-black/40 rounded-2xl border border-white/5">
         <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-cyan-500/10 flex items-center justify-center text-cyan-400">
                <ArrowRight size={24} />
            </div>
            <div>
                <p className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Reallocation Thesis</p>
                <p className="text-xs text-slate-500 leading-relaxed italic mt-1">
                    "The 2026 data confirms labor is not disappearing, but coagulating around **AI Governance Nodes**. Success requires shifting from execution to orchestration."
                </p>
            </div>
         </div>
      </div>
    </div>
  );
};

export default LaborFlowSankey;
