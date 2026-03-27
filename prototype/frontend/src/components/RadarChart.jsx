import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const SkillRadarChart = ({ userData }) => {
  // Benchmark for a "Strategic Orchestrator"
  const benchmarkData = [
    { subject: 'Theoretical Exposure', A: 85, fullMark: 100 },
    { subject: 'Automation Resilience', A: 90, fullMark: 100 },
    { subject: 'Task Codifiability', A: 20, fullMark: 100 },
    { subject: 'Skill Transferability', A: 95, fullMark: 100 },
    { subject: 'AI Maturity', A: 80, fullMark: 100 },
  ];

  // Map user data to the same structure
  const processedData = [
    { subject: 'Theoretical Exposure', A: 85, B: userData.theoretical_exposure_pct || 50, fullMark: 100 },
    { subject: 'Automation Resilience', A: 90, B: (userData.resilience_score * 5) || 30, fullMark: 100 },
    { subject: 'Task Codifiability', A: 20, B: (userData.task_codifiability_score * 100) || 60, fullMark: 100 },
    { subject: 'Skill Transferability', A: 95, B: (userData.skill_transferability_score * 100) || 40, fullMark: 100 },
    { subject: 'AI Maturity', A: 80, B: (userData.org_ai_maturity_stage * 20) || 20, fullMark: 100 },
  ];

  return (
    <div className="bg-slate-900/50 p-6 rounded-2xl border border-white/10 h-[400px]">
      <h3 className="text-sm font-bold text-slate-400 mb-4 uppercase tracking-widest">Skill Multi-Dimensional Matrix</h3>
      <ResponsiveContainer width="100%" height="90%">
        <RadarChart cx="50%" cy="50%" outerRadius="80%" data={processedData}>
          <PolarGrid stroke="#334155" />
          <PolarAngleAxis dataKey="subject" tick={{ fill: '#94a3b8', fontSize: 10 }} />
          <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} />
          <Radar
            name="Strategic Orchestrator (Bench)"
            dataKey="A"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.3}
          />
          <Radar
            name="Your Profile"
            dataKey="B"
            stroke="#3b82f6"
            fill="#3b82f6"
            fillOpacity={0.6}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#0f172a', border: '1px solid #334155', borderRadius: '8px' }}
            itemStyle={{ color: '#f8fafc' }}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default SkillRadarChart;
