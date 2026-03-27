import React from "react"

// Simulated Grid Map for the "Command Center"
const GlobalRiskMap = () => {
  // Mock Risk Centers
  const hotspots = [
    { name: "North America", x: 150, y: 100, risk: 78, status: "Critical" },
    { name: "Western Europe", x: 380, y: 90, risk: 72, status: "High" },
    { name: "East Asia", x: 650, y: 110, risk: 84, status: "Hyper-Risk" },
    { name: "Southeast Asia", x: 620, y: 220, risk: 65, status: "Vulnerable" },
    { name: "Oceania", x: 700, y: 300, risk: 45, status: "Stable" },
  ];

  return (
    <div className="bg-slate-900/50 p-6 rounded-3xl border border-white/10 h-[450px] overflow-hidden relative group">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest">Global Displacement Matrix</h3>
          <p className="text-[10px] text-slate-500 font-mono mt-1 uppercase tracking-tighter">Real-time Geographic Vulnerability Sync</p>
        </div>
        <div className="px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-md text-red-400 text-[10px] font-bold animate-pulse">
          LIVE TELEMETRY
        </div>
      </div>

      <div className="relative h-[320px] w-full flex items-center justify-center bg-black/40 rounded-2xl border border-white/5 overflow-hidden">
        {/* Cyber Grid Background */}
        <svg width="100%" height="100%" className="opacity-30">
          <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" strokeWidth="0.5" />
          </pattern>
          <rect width="100%" height="100%" fill="url(#grid)" />
          
          {/* Abstract World Outlines (Dots) */}
          {Array.from({ length: 40 }).map((_, i) => (
            Array.from({ length: 20 }).map((_, j) => {
              // Simple logic to "draw" landmasses roughly
              const isLand = (i > 5 && i < 12 && j > 3 && j < 10) || // Americas
                             (i > 18 && i < 25 && j > 2 && j < 8) || // Europe/Africa
                             (i > 28 && i < 38 && j > 4 && j < 12);  // Asia
              if (!isLand) return null;
              return (
                <circle 
                  key={`${i}-${j}`} 
                  cx={i * 20 + 10} cy={j * 20 + 10} r="1.5" 
                  fill="#334155" 
                />
              )
            })
          ))}

          {/* Connectors */}
          <line x1="150" y1="100" x2="380" y2="90" stroke="#00f3ff" strokeWidth="0.5" strokeDasharray="4 4" className="animate-pulse" />
          <line x1="380" y1="90" x2="650" y2="110" stroke="#00f3ff" strokeWidth="0.5" strokeDasharray="4 4" className="animate-pulse" />
        </svg>

        {/* Hotspots */}
        {hotspots.map((spot) => (
          <div 
            key={spot.name}
            className="absolute flex flex-col items-center group/spot cursor-help"
            style={{ left: spot.x, top: spot.y }}
          >
            <div className={`w-4 h-4 rounded-full border-2 border-white shadow-xl ${spot.risk > 75 ? 'bg-red-500 shadow-red-500/50' : 'bg-cyan-500 shadow-cyan-500/50'} animate-ping opacity-75 absolute`}></div>
            <div className={`w-4 h-4 rounded-full border-2 border-white relative ${spot.risk > 75 ? 'bg-red-500' : 'bg-cyan-500'}`}></div>
            
            {/* Tooltip */}
            <div className="absolute top-full mt-2 bg-slate-950 border border-white/10 p-3 rounded-xl opacity-0 group-hover/spot:opacity-100 transition-opacity z-20 pointer-events-none w-48 shadow-2xl">
              <div className="text-[10px] font-bold text-slate-500 uppercase mb-1">{spot.name}</div>
              <div className="flex justify-between items-center">
                <span className="text-xs font-black text-white">{spot.status}</span>
                <span className="text-xs font-mono text-cyan-400">{spot.risk}%</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full mt-2">
                <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${spot.risk}%` }}></div>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex justify-between items-end">
         <div className="flex gap-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-red-500"></div>
              <span className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Aggressive Deployment</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-cyan-500"></div>
              <span className="text-[10px] text-slate-500 uppercase font-bold tracking-widest">Steady Integration</span>
            </div>
         </div>
         <p className="text-[9px] font-mono text-slate-600 max-w-[200px] text-right italic">
           *Grounding data sourced from 2026 OECD AI Adoption Projections.
         </p>
      </div>
    </div>
  )
}

export default GlobalRiskMap;
