import React from 'react';
import { motion } from 'framer-motion';
import { TrendingUp, ShieldCheck, ArrowRight, Lightbulb } from 'lucide-react';

const ResilienceRoadmap = ({ gapData }) => {
  if (!gapData) return null;

  const { salary_premium, codifiability_reduction_pct, gaps } = gapData;

  const cards = [
    {
      title: "Strategic Salary Premium",
      value: `$${(salary_premium / 1000).toFixed(1)}k`,
      subtitle: "Annual yield for full competency",
      icon: TrendingUp,
      color: "text-emerald-400",
      bg: "bg-emerald-500/10",
      border: "border-emerald-500/20",
      detail: "Based on real-world income delta for AI-augmented roles in your sector."
    },
    {
      title: "Substitution Shield",
      value: `${codifiability_reduction_pct}%`,
      subtitle: "Reduction in task codifiability",
      icon: ShieldCheck,
      color: "text-cyan-400",
      bg: "bg-cyan-500/10",
      border: "border-cyan-500/20",
      detail: "Strategic skills shift you from 'Operator' to 'Governor' of AI systems."
    }
  ];

  return (
    <div className="space-y-6">
      <h3 className="text-[10px] font-bold text-slate-400 mb-4 uppercase tracking-[0.3em] flex items-center gap-2">
        <Lightbulb size={12} className="text-yellow-400" />
        Resilience Reallocation Roadmap
      </h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {cards.map((card, idx) => (
          <motion.div 
            key={card.title}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className={`p-6 rounded-3xl border ${card.border} ${card.bg} backdrop-blur-md group hover:bg-white/5 transition-all`}
          >
            <div className="flex justify-between items-start mb-4">
              <div className={`p-2 rounded-xl ${card.bg} border ${card.border}`}>
                <card.icon size={18} className={card.color} />
              </div>
              <span className="text-[8px] text-slate-500 font-mono uppercase tracking-widest">Calculated Logic</span>
            </div>
            
            <div className={`text-3xl font-black ${card.color} mb-1 tracking-tighter`}>{card.value}</div>
            <div className="text-[10px] font-bold text-white uppercase tracking-wider mb-2">{card.title}</div>
            <p className="text-[10px] text-slate-400 leading-relaxed italic">"{card.detail}"</p>
          </motion.div>
        ))}
      </div>

      <div className="p-6 bg-slate-900/40 rounded-3xl border border-white/5">
        <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-4">Urgent Upskilling Priority</div>
        <div className="space-y-3">
          {Object.entries(gaps).filter(([k, v]) => v > 0).map(([skill, gap]) => (
             <div key={skill} className="flex items-center justify-between p-3 bg-black/20 rounded-xl border border-white/5 group hover:border-cyan-500/20 transition-all">
                <div className="flex items-center gap-3">
                   <div className="w-1.5 h-1.5 rounded-full bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.6)]" />
                   <span className="text-xs font-mono text-slate-300">{skill.replace('skills_', '').replace('_', ' ').toUpperCase()}</span>
                </div>
                <div className="flex items-center gap-2">
                   <span className="text-[10px] font-bold text-rose-400">{(gap * 100).toFixed(0)}% DEFICIT</span>
                   <ArrowRight size={12} className="text-slate-600 group-hover:translate-x-1 transition-transform" />
                </div>
             </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ResilienceRoadmap;
