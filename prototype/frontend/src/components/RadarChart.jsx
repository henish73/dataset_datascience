import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const SkillRadarChart = ({ gapData }) => {
  if (!gapData || !gapData.benchmark) {
    return (
      <div className="bg-slate-900/50 p-6 rounded-2xl border border-white/10 h-[400px] flex items-center justify-center">
        <p className="text-slate-500 font-mono text-xs animate-pulse">Awaiting Competency Telemetry...</p>
      </div>
    );
  }

  const { benchmark, user_competencies } = gapData;

  const processedData = [
    { subject: 'Python Fluency', A: benchmark.skills_python * 100, B: user_competencies.skills_python * 100, fullMark: 100 },
    { subject: 'Cloud Arch', A: benchmark.skills_cloud * 100, B: user_competencies.skills_cloud * 100, fullMark: 100 },
    { subject: 'Deep Learning', A: benchmark.skills_deep_learning * 100, B: user_competencies.skills_deep_learning * 100, fullMark: 100 },
    { subject: 'Resilience Index', A: benchmark.resilience_score * 5, B: user_competencies.resilience_score * 5, fullMark: 100 },
  ];

  return (
    <div className="bg-slate-900/50 p-6 rounded-3xl border border-white/5 h-[450px] shadow-2xl backdrop-blur-xl">
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.3em]">Competency Void Matrix</h3>
        <span className="text-[10px] bg-cyan-500/10 text-cyan-400 px-2 py-0.5 rounded border border-cyan-500/20 font-mono">
            {gapData.sector_context}
        </span>
      </div>
      
      <ResponsiveContainer width="100%" height="80%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={processedData}>
          <PolarGrid stroke="#334155" strokeDasharray="3 3" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10, fontWeight: 700 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} stroke="transparent" />
          
          <Tooltip 
             contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '12px', fontSize: '10px' }}
             itemStyle={{ color: '#f8fafc', padding: '2px 0' }}
             cursor={{ stroke: '#3b82f6', strokeWidth: 1 }}
          />

          <Radar
            name="Shielded Benchmark"
            dataKey="A"
            stroke="#10b981"
            fill="#10b981"
            fillOpacity={0.15}
            strokeWidth={2}
          />
          <Radar
            name="Your Profile"
            dataKey="B"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.5}
            strokeWidth={3}
          />
          <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '20px', color: '#94a3b8' }} />
        </RadarChart>
      </ResponsiveContainer>
      
      <div className="mt-4 pt-4 border-t border-white/5 flex justify-around text-center">
        {processedData.map(d => {
            const gap = d.A - d.B;
            return gap > 10 ? (
                <div key={d.subject} className="flex flex-col">
                    <span className="text-[8px] text-slate-500 uppercase font-bold">{d.subject} GAP</span>
                    <span className="text-xs font-black text-rose-400 animate-pulse">-{gap.toFixed(0)}%</span>
                </div>
            ) : null;
        })}
      </div>
    </div>
  );
};

export default SkillRadarChart;
