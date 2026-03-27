import React from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

const RiskScatterPlot = () => {
  // Sample data simulating the K-Shape Divergence from the master dataset
  const data = [
    { x: 145000, y: 38.8, name: 'Strategic Orchestrator', role: 'Data Architect', res: 18.2 },
    { x: 128000, y: 42.1, name: 'Strategic Orchestrator', role: 'AI Consultant', res: 17.5 },
    { x: 82000, y: 56.8, name: 'Middle-Mgmt', role: 'Operations Coordinator', res: 8.4 },
    { x: 74000, y: 62.4, name: 'Middle-Mgmt', role: 'Legal Assistant', res: 6.2 },
    { x: 55000, y: 74.9, name: 'Remote Roles', role: 'Accountant', res: 4.1 },
    { x: 48000, y: 78.2, name: 'Remote Roles', role: 'Translator', res: 3.8 },
    { x: 160000, y: 25.0, name: 'On-Site Specialist', role: 'Surgeon', res: 19.1 },
    { x: 42000, y: 22.1, name: 'On-Site Specialist', role: 'Plumber', res: 14.5 },
    { x: 110000, y: 48.5, name: 'Middle-Mgmt', role: 'Project Manager', res: 9.2 },
    { x: 135000, y: 31.2, name: 'Strategic Orchestrator', role: 'Policy Analyst', res: 16.8 },
  ];

  return (
    <div className="bg-slate-900/50 p-6 rounded-2xl border border-white/10 h-[400px]">
      <h3 className="text-sm font-bold text-slate-400 mb-4 uppercase tracking-widest">The K-Shape Divergence Map</h3>
      <ResponsiveContainer width="100%" height="90%">
        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
          <XAxis type="number" dataKey="x" name="Salary" unit=" $" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} domain={['auto', 'auto']} />
          <YAxis type="number" dataKey="y" name="Risk" unit="%" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
          <ZAxis type="number" dataKey="res" range={[50, 400]} name="Resilience" />
          <Tooltip 
            cursor={{ strokeDasharray: '3 3' }} 
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                return (
                  <div className="bg-slate-950 border border-slate-800 p-3 rounded-xl shadow-2xl">
                    <p className="text-blue-400 font-bold text-xs uppercase tracking-wider">{item.name}</p>
                    <p className="text-white text-sm font-medium">{item.role}</p>
                    <div className="mt-2 text-[10px] text-slate-400 space-y-1">
                      <p>Salary: ${item.x.toLocaleString()}</p>
                      <p>Automation Risk: {item.y}%</p>
                      <p>Resilience Score: {item.res}</p>
                    </div>
                  </div>
                );
              }
              return null;
            }}
          />
          <Scatter name="Labor Market" data={data}>
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={entry.y > 60 ? '#ef4444' : entry.y > 40 ? '#f59e0b' : '#22c55e'} 
                fillOpacity={0.7}
                strokeWidth={2}
                stroke={entry.y > 60 ? '#7f1d1d' : entry.y > 40 ? '#78350f' : '#14532d'}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>
    </div>
  );
};

export default RiskScatterPlot;
