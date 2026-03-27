import { useState, useMemo } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Activity, ShieldAlert, ShieldCheck, Zap, Server, Network, 
  LayoutDashboard, BarChart3, Globe, BookOpen, Search, Info
} from 'lucide-react';

// New Components
import SkillRadarChart from './components/RadarChart';
import RiskScatterPlot from './components/RiskScatterPlot';
import GlobalRiskMap from './components/GlobalRiskMap';

function App() {
  const [activeTab, setActiveTab ] = useState('navigator');
  const [formData, setFormData] = useState({
    theoretical_exposure_pct: 60,
    annual_salary_usd: 120000,
    education_mismatch_idx: 0.3,
    is_remote_eligible: 1,
    is_senior: 0,
    resilience_score: 10,
    task_codifiability_score: 0.6,
    skill_transferability_score: 0.5,
    org_ai_maturity_stage: 3,
    chance_of_automation_onet: 50
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  // Research Findings (Distilled from StatCan/WEF/O*NET analysis)
  const researchFindings = [
    { id: 1, source: "WEF 2025", topic: "The K-Shape", detail: "High-income roles leverage AI for 40% productivity gains while middle-management faces 56% task automation." },
    { id: 2, source: "StatCan 2026", topic: "Remote Penalty", detail: "Remote-eligible roles exhibit a 74.9% displacement rate due to digital task codifiability." },
    { id: 3, source: "O*NET Analysis", topic: "Skill Shielding", detail: "Proficiency in 'Complex Problem Solving' and 'AI Orchestration' reduces displacement risk by 30%." },
    { id: 4, source: "WEF 2025", topic: "Coordination Tax", detail: "AI systems are specifically targeting the 'Efficiency Delta' in middle-management coordination workflows." },
  ];

  const filteredFindings = researchFindings.filter(f => 
    f.topic.toLowerCase().includes(searchQuery.toLowerCase()) || 
    f.detail.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? (checked ? 1 : 0) : parseFloat(value)
    }));
  };

  const handleCalculate = async () => {
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/predict', formData);
      setResult(response.data);
    } catch (error) {
      console.error("Prediction Error: ", error);
      alert("Error connecting to the Prediction Simulator Backend. Ensure the FastAPI server is running on Port 8000.");
    }
    setLoading(false);
  };

  const getRiskStyles = (zone) => {
    if (zone === "Red Zone") return { color: "text-[#ff003c]", border: "border-[#ff003c]", shadow: "shadow-neon-red", bg: "bg-[#ff003c]/10" };
    if (zone === "Green Zone") return { color: "text-[#00ff66]", border: "border-[#00ff66]", shadow: "shadow-neon-green", bg: "bg-[#00ff66]/10" };
    return { color: "text-[#ffcc00]", border: "border-[#ffcc00]", shadow: "shadow-neon-yellow", bg: "bg-[#ffcc00]/10" };
  };

  const activeStyle = result ? getRiskStyles(result.zone) : null;

  return (
    <div className="min-h-screen bg-[#020617] text-gray-200 font-sans relative overflow-hidden flex flex-col">
      
      {/* Background FX */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-900/10 blur-[120px] rounded-full pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-900/10 blur-[120px] rounded-full pointer-events-none"></div>

      {/* Sidebar Navigation */}
      <nav className="fixed left-0 top-0 bottom-0 w-20 bg-black/40 border-r border-white/5 flex flex-col items-center py-10 z-50 gap-8">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center mb-4 shadow-lg shadow-cyan-500/20">
          <Zap className="text-white" size={24} fill="currentColor" />
        </div>
        
        {[
          { id: 'navigator', icon: LayoutDashboard, label: 'Predictor' },
          { id: 'intelligence', icon: BarChart3, label: 'Intelligence' },
          { id: 'geographic', icon: Globe, label: 'Geo-Map' },
          { id: 'research', icon: BookOpen, label: 'Research' }
        ].map((btn) => (
          <button 
            key={btn.id}
            onClick={() => setActiveTab(btn.id)}
            className={`p-3 rounded-xl transition-all duration-300 relative group ${activeTab === btn.id ? 'bg-white/10 text-cyan-400' : 'text-slate-500 hover:text-white'}`}
          >
            <btn.icon size={24} />
            <span className="absolute left-full ml-4 px-2 py-1 bg-slate-800 text-[10px] rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap uppercase tracking-widest border border-white/10">
              {btn.label}
            </span>
            {activeTab === btn.id && <motion.div layoutId="nav-active" className="absolute left-0 top-0 bottom-0 w-1 bg-cyan-400 rounded-full" />}
          </button>
        ))}
      </nav>

      {/* Main Content Area */}
      <main className="ml-20 flex-1 p-8 overflow-y-auto">
        
        {/* Top Header */}
        <header className="flex justify-between items-center mb-12">
          <div>
            <h1 className="text-3xl font-black text-white tracking-tight flex items-center gap-3">
              <span className="px-2 py-1 bg-cyan-500/10 border border-cyan-500/20 rounded-md text-cyan-400 text-xs font-mono">V2.0 ENSEMBLE</span>
              Labor Risk Navigator
            </h1>
            <p className="text-slate-500 font-mono text-xs uppercase tracking-[0.3em] mt-1">Multi-Model Adaptive Telemetry Dashboard</p>
          </div>
          
          <div className="flex gap-4">
            <div className="flex flex-col items-end">
              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Consensus Status</span>
              <span className="text-xs text-green-400 font-mono flex items-center gap-2">
                <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span> SYSTEM NOMINAL
              </span>
            </div>
          </div>
        </header>

        <AnimatePresence mode="wait">
          {activeTab === 'navigator' && (
            <motion.div 
              key="navigator" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
              className="grid grid-cols-12 gap-8"
            >
              {/* Left Form */}
              <div className="col-span-12 lg:col-span-7 space-y-8 bg-slate-900/40 p-10 rounded-3xl border border-white/5 shadow-inner">
                <h2 className="text-sm font-bold text-slate-400 flex items-center gap-3 uppercase tracking-[0.2em] mb-4">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full"></div> Input Matrix
                </h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-x-12 gap-y-8">
                  {[
                    { label: 'Exposure (%)', name: 'theoretical_exposure_pct', min: 0, max: 100, step: 1, suffix: '%' },
                    { label: 'Salary (USD)', name: 'annual_salary_usd', min: 30000, max: 250000, step: 5000, pre: '$' },
                    { label: 'Skill Gap', name: 'education_mismatch_idx', min: 0, max: 1, step: 0.05 },
                    { label: 'Resilience', name: 'resilience_score', min: 0, max: 20, step: 0.5 },
                  ].map((input) => (
                    <div key={input.name} className="group">
                      <label className="flex justify-between text-[10px] font-bold text-slate-500 mb-3 uppercase tracking-widest group-hover:text-slate-300 transition-colors">
                        {input.label}
                        <span className="text-cyan-400 font-mono text-xs bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/20">
                          {input.pre}{input.name === 'annual_salary_usd' ? formData[input.name].toLocaleString() : formData[input.name]}{input.suffix}
                        </span>
                      </label>
                      <input 
                        type="range" name={input.name} min={input.min} max={input.max} step={input.step} 
                        value={formData[input.name]} onChange={handleChange} 
                        className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                      />
                    </div>
                  ))}
                </div>

                <div className="flex gap-12 pt-8 border-t border-white/5">
                   <label className="flex items-center gap-3 cursor-pointer group">
                      <div className="relative">
                        <input type="checkbox" name="is_remote_eligible" checked={formData.is_remote_eligible === 1} onChange={handleChange} className="sr-only peer" />
                        <div className="w-10 h-5 bg-slate-800 rounded-full peer peer-checked:bg-purple-500 transition-colors border border-white/5"></div>
                        <div className="absolute left-1 top-1 bg-white w-3 h-3 rounded-full transition-all peer-checked:translate-x-5"></div>
                      </div>
                      <span className="text-[10px] uppercase font-bold tracking-widest text-slate-500 group-hover:text-slate-200">Remote eligible</span>
                    </label>
                    <label className="flex items-center gap-3 cursor-pointer group">
                      <div className="relative">
                        <input type="checkbox" name="is_senior" checked={formData.is_senior === 1} onChange={handleChange} className="sr-only peer" />
                        <div className="w-10 h-5 bg-slate-800 rounded-full peer peer-checked:bg-cyan-500 transition-colors border border-white/5"></div>
                        <div className="absolute left-1 top-1 bg-white w-3 h-3 rounded-full transition-all peer-checked:translate-x-5"></div>
                      </div>
                      <span className="text-[10px] uppercase font-bold tracking-widest text-slate-500 group-hover:text-slate-200">Senior Orchestrator</span>
                    </label>
                </div>

                <button 
                  onClick={handleCalculate} disabled={loading}
                  className="w-full py-5 rounded-2xl font-black bg-white text-black hover:bg-cyan-400 transition-all duration-500 uppercase tracking-[0.3em] text-[10px] shadow-xl hover:shadow-cyan-400/20 active:scale-[0.98]"
                >
                  <span className="flex items-center justify-center gap-3">
                    {loading ? <Activity className="animate-spin" size={16} /> : <Zap size={16} />}
                    {loading ? 'Processing Model Consensus...' : 'Run Prediction Engine'}
                  </span>
                </button>
              </div>

              {/* Right Output */}
              <div className="col-span-12 lg:col-span-5 flex flex-col gap-6">
                <div className="bg-slate-900/60 p-10 rounded-3xl border border-white/5 flex-1 relative flex flex-col items-center justify-center text-center">
                  {result ? (
                    <>
                      <div className={`text-7xl font-black mb-2 tracking-tighter ${activeStyle.color}`}>
                        {result.displacement_probability_pct}%
                      </div>
                      <div className="text-[10px] text-slate-500 uppercase font-mono tracking-[0.4em] mb-8">Consensus Risk Score</div>
                      
                      <div className={`px-6 py-4 rounded-2xl border ${activeStyle.bg} ${activeStyle.border} w-full`}>
                        <div className="text-[10px] uppercase tracking-widest font-bold text-slate-400 mb-2">Neural Inference</div>
                        <div className={`text-sm font-black uppercase text-white tracking-widest`}>{result.resilience_category}</div>
                      </div>

                      <div className="mt-8 p-4 bg-black/40 rounded-xl border border-white/5 w-full text-left">
                        <div className="flex items-center gap-2 mb-2">
                           <Info size={12} className="text-cyan-400" />
                           <span className="text-[10px] font-bold text-slate-500 uppercase tracking-widest">SHAP Reasoning</span>
                        </div>
                        <p className="text-xs text-slate-300 italic">"{result.reasoning_summary}"</p>
                      </div>
                    </>
                  ) : (
                    <div className="opacity-20 animate-pulse text-slate-500">
                      <Activity size={80} strokeWidth={1} />
                      <p className="mt-4 font-mono text-[10px] tracking-widest">SYSTEM STANDBY</p>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'intelligence' && (
            <motion.div 
              key="intelligence" initial={{ opacity: 0, scale: 0.98 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.98 }}
              className="grid grid-cols-1 lg:grid-cols-2 gap-8"
            >
              <div className="col-span-1">
                <SkillRadarChart userData={formData} />
              </div>
              <div className="col-span-1">
                <RiskScatterPlot />
              </div>
              <div className="col-span-2 p-6 bg-slate-900/40 rounded-3xl border border-white/5">
                <div className="flex items-center gap-4 mb-4">
                  <Info className="text-purple-400" />
                  <h3 className="text-sm font-bold uppercase tracking-[0.2em] text-slate-300">The K-Shape Hypothesis</h3>
                </div>
                <p className="text-sm text-slate-500 leading-relaxed">
                  Our multi-model ensemble confirms the emergence of a dual-track labor market. High-level **Strategic Orchestrators** (Green Zone) utilize agentic AI to amplify their cognitive reach, while **Middle-Management Coordinators** (Yellow/Red Zone) face structural displacement as AI absorbs routine oversight and scheduling logic.
                </p>
              </div>
            </motion.div>
          )}

          {activeTab === 'geographic' && (
            <motion.div 
              key="geographic" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="space-y-8"
            >
              <GlobalRiskMap />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { region: 'NA Market', risk: 'Critical', color: 'text-red-400', desc: 'High emphasis on digital service coordination.' },
                  { region: 'EMEA', risk: 'Transition', color: 'text-yellow-400', desc: 'Labor protections delaying systemic displacement.' },
                  { region: 'APAC', risk: 'Emerging', color: 'text-blue-400', desc: 'Rapid adoption of AI nodes in manufacturing.' }
                ].map(r => (
                  <div key={r.region} className="p-6 bg-slate-900/60 rounded-2xl border border-white/5">
                    <div className="text-[10px] font-bold text-slate-500 uppercase tracking-widest mb-1">{r.region}</div>
                    <div className={`text-lg font-black uppercase tracking-wider ${r.color}`}>{r.risk}</div>
                    <p className="text-[10px] text-slate-500 mt-2">{r.desc}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          {activeTab === 'research' && (
            <motion.div 
              key="research" initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 10 }}
              className="space-y-8"
            >
              <div className="relative">
                <Search className="absolute left-6 top-1/2 -translate-y-1/2 text-slate-500" size={20} />
                <input 
                  type="text" 
                  placeholder="Search Research Context Database (e.g. 'K-Shape', 'Remote', 'OECD')..." 
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-900/60 border border-white/5 rounded-2xl py-6 pl-16 pr-6 text-sm outline-none focus:border-cyan-500/50 transition-all font-mono"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {filteredFindings.map(finding => (
                  <div key={finding.id} className="p-8 bg-slate-900/40 rounded-3xl border border-white/5 hover:border-cyan-500/20 transition-all group">
                    <div className="flex justify-between items-start mb-4">
                      <span className="px-2 py-1 bg-white/5 rounded text-[10px] font-mono text-slate-400 group-hover:text-cyan-400 transition-colors uppercase tracking-widest">
                        {finding.source}
                      </span>
                      <BookOpen size={16} className="text-slate-600 group-hover:text-cyan-400 transition-colors" />
                    </div>
                    <h3 className="text-lg font-black text-white mb-2 uppercase tracking-wide">{finding.topic}</h3>
                    <p className="text-sm text-slate-500 leading-relaxed font-serif italic">"{finding.detail}"</p>
                  </div>
                ))}
              </div>

              <div className="p-10 bg-gradient-to-br from-slate-900 to-black rounded-3xl border border-white/10 mt-12">
                <h3 className="text-xl font-black text-white mb-6 uppercase tracking-[0.2em]">Synthesis Methodology</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-sm">
                  <div>
                    <div className="text-cyan-400 font-black text-3xl mb-2">01</div>
                    <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-4">O*NET Grounding</p>
                    <p className="text-slate-500 leading-relaxed">Cross-referencing 45 unique task-based O*NET datasets to establish baseline automation probability for structural occupations.</p>
                  </div>
                  <div>
                    <div className="text-purple-400 font-black text-3xl mb-2">02</div>
                    <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-4">Market Interpolation</p>
                    <p className="text-slate-500 leading-relaxed">Applying 2025/2026 market trends from WEF and StatCan to weigh the impact of salary brackets and remote eligibility multipliers.</p>
                  </div>
                  <div>
                    <div className="text-pink-400 font-black text-3xl mb-2">03</div>
                    <p className="text-slate-400 font-bold uppercase tracking-widest text-xs mb-4">Ensemble Simulation</p>
                    <p className="text-slate-500 leading-relaxed">Running input vectors through our XGBoost, RF, and MLP ensemble to generate high-precision displacement probabilities.</p>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}

export default App;
