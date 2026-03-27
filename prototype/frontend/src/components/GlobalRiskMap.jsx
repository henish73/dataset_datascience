import React, { useEffect, useState, useMemo } from "react"
import * as d3 from "d3-geo"
import { feature } from "topojson-client"

// TopoJSON source (Very small, ~50KB)
const geoUrl = "https://unpkg.com/world-atlas@2.0.2/countries-110m.json";

const GlobalRiskMap = () => {
  const [geographies, setGeographies] = useState([]);
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);

  // Map dimensions
  const width = 800;
  const height = 320;

  // Projection setup
  const projection = useMemo(() => {
    return d3.geoMercator()
      .scale(100)
      .translate([width / 2, height / 2 + 40]);
  }, [width, height]);

  const pathGenerator = d3.geoPath().projection(projection);

  useEffect(() => {
    // Fetch Map Data and Risk Data concurrently
    Promise.all([
      fetch(geoUrl).then(res => res.json()),
      fetch('http://localhost:8000/global-risk').then(res => res.json())
    ])
    .then(([geoData, riskData]) => {
      const countries = feature(geoData, geoData.objects.countries).features;
      setGeographies(countries);
      if (riskData && riskData.hotspots) {
        setHotspots(riskData.hotspots);
      }
      setLoading(false);
    })
    .catch(err => {
      console.error("Error loading map or risk data:", err);
      setLoading(false);
    });
  }, []);

  return (
    <div className="bg-slate-900/50 p-6 rounded-3xl border border-white/10 h-[450px] overflow-hidden relative group font-sans">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-sm font-bold text-slate-300 uppercase tracking-widest">Global Displacement Matrix</h3>
          <p className="text-[10px] text-slate-500 font-mono mt-1 uppercase tracking-tighter">Real-time Geographic Vulnerability Sync</p>
        </div>
        <div className="px-3 py-1 bg-red-500/10 border border-red-500/20 rounded-md text-red-400 text-[10px] font-bold animate-pulse">
          LIVE TELEMETRY
        </div>
      </div>

      <div className="relative h-[320px] w-full bg-black/40 rounded-2xl border border-white/5 overflow-hidden">
        {/* Cyber Grid Overlay */}
        <div className="absolute inset-0 pointer-events-none opacity-10">
          <svg width="100%" height="100%">
            <pattern id="grid-pattern" width="30" height="30" patternUnits="userSpaceOnUse">
              <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" strokeWidth="0.5" />
            </pattern>
            <rect width="100%" height="100%" fill="url(#grid-pattern)" />
          </svg>
        </div>

        {loading ? (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-8 h-8 border-2 border-cyan-500/20 border-t-cyan-500 rounded-full animate-spin"></div>
          </div>
        ) : (
          <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
            <g>
              {geographies.map((geo, index) => (
                <path
                  key={`path-${index}`}
                  d={pathGenerator(geo)}
                  fill="#0f172a"
                  stroke="#1e293b"
                  strokeWidth="0.5"
                  className="transition-colors duration-300 hover:fill-[#1e293b] cursor-default"
                />
              ))}
            </g>

            {hotspots.map((spot) => {
              const [x, y] = projection(spot.coordinates);
              return (
                <g key={spot.name} className="group/marker cursor-help">
                  {/* Ping effect */}
                  <circle
                    cx={x} cy={y}
                    r={6}
                    fill={spot.risk > 75 ? "#ef4444" : "#06b6d4"}
                    className="animate-ping opacity-40"
                  />
                  {/* Main dot */}
                  <circle
                    cx={x} cy={y}
                    r={4}
                    fill={spot.risk > 75 ? "#ef4444" : "#06b6d4"}
                    stroke="#ffffff"
                    strokeWidth={1.5}
                    className="shadow-xl"
                  />
                  
                  {/* Tooltip implementation using foreignObject for HTML/Tailwind support */}
                  <foreignObject x={x + 10} y={y - 40} width="160" height="80" className="overflow-visible opacity-0 group-hover/marker:opacity-100 transition-opacity pointer-events-none">
                    <div className="bg-slate-950/90 border border-white/10 p-2 rounded-lg shadow-2xl backdrop-blur-sm">
                      <div className="text-[9px] font-bold text-slate-500 uppercase mb-0.5">{spot.name}</div>
                      <div className="flex justify-between items-center">
                        <span className="text-[10px] font-black text-white">{spot.status}</span>
                        <span className="text-[10px] font-mono text-cyan-400">{spot.risk}%</span>
                      </div>
                      <div className="w-full bg-slate-800 h-1 rounded-full mt-1.5 overflow-hidden">
                        <div 
                          className={`h-full ${spot.risk > 75 ? "bg-red-500" : "bg-cyan-500"}`} 
                          style={{ width: `${spot.risk}%` }}
                        ></div>
                      </div>
                    </div>
                  </foreignObject>
                </g>
              );
            })}
          </svg>
        )}
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
