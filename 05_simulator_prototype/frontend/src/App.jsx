import { useState } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, ShieldAlert, ShieldCheck, Zap, Server, Network } from 'lucide-react';

function App() {
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
      // Connect to the local FastAPI backend
      const response = await axios.post('http://localhost:8000/predict', formData);
      setResult(response.data);
    } catch (error) {
      console.error("Prediction Error: ", error);
      alert("Error connecting to the Prediction Simulator Backend. Ensure the FastAPI server is running on Port 8000.");
    }
    setLoading(false);
  };

  const getRiskStyles = (zone) => {
    if (zone === "Red Zone") return {
      color: "text-[#ff003c]",
      border: "border-[#ff003c]",
      shadow: "shadow-neon-red",
      bg: "bg-[#ff003c]/10"
    };
    if (zone === "Green Zone") return {
      color: "text-[#00ff66]",
      border: "border-[#00ff66]",
      shadow: "shadow-neon-green",
      bg: "bg-[#00ff66]/10"
    };
    return {
      color: "text-[#ffcc00]",
      border: "border-[#ffcc00]",
      shadow: "shadow-[0_0_15px_#ffcc00]",
      bg: "bg-[#ffcc00]/10"
    };
  };

  const activeStyle = result ? getRiskStyles(result.zone) : null;

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#020617] text-gray-200 font-sans relative overflow-hidden p-6">
      
      {/* Animated Background Gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-900/20 blur-[120px] rounded-full mix-blend-screen animate-pulse pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-900/20 blur-[120px] rounded-full mix-blend-screen animate-pulse pointer-events-none" style={{ animationDelay: '2s' }}></div>
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5 pointer-events-none"></div>

      <motion.div 
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
        className="max-w-5xl w-full z-10"
      >
        <div className="backdrop-blur-xl bg-[#0b1120]/80 border border-white/10 shadow-2xl rounded-3xl overflow-hidden flex flex-col">
          
          {/* Header */}
          <header className="px-10 py-8 border-b border-white/5 flex items-center justify-between bg-gradient-to-r from-black/20 to-transparent">
            <div>
              <h1 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-[#00f3ff] to-[#bc13fe] tracking-tight flex items-center gap-4">
                <Network className="text-[#00f3ff]" size={40} strokeWidth={1.5} />
                2026 Labor Risk Navigator
              </h1>
              <p className="text-gray-400 mt-2 font-mono text-sm tracking-widest uppercase flex items-center gap-2">
                <Server size={14} className="text-[#bc13fe]" /> AI-Labor Paradox Simulator
              </p>
            </div>
            
            {/* Status Indicator */}
            <div className="flex items-center gap-3 px-4 py-2 rounded-full bg-black/40 border border-white/10">
              <span className={`w-3 h-3 rounded-full ${result ? (result.zone === 'Red Zone' ? 'bg-[#ff003c] animate-pulse' : 'bg-[#00ff66]') : 'bg-gray-500'}`}></span>
              <span className="text-xs font-mono text-gray-300 uppercase">{result ? 'Telemetry Active' : 'Awaiting Input'}</span>
            </div>
          </header>

          <div className="grid grid-cols-1 lg:grid-cols-12">
            
            {/* LEFT: Inputs (7 cols) */}
            <div className="p-10 lg:col-span-7 bg-white/[0.02]">
              <h2 className="text-xl font-bold text-white mb-8 flex items-center gap-3">
                <span className="w-8 h-px bg-[#00f3ff]"></span> Matrix Configuration
              </h2>
              
              <div className="space-y-8">
                {/* Sliders */}
                {[
                  { label: 'Automation Exposure (%)', name: 'theoretical_exposure_pct', min: 0, max: 100, step: 1, suffix: '%' },
                  { label: 'Annual Salary (USD)', name: 'annual_salary_usd', min: 30000, max: 250000, step: 5000, pre: '$', suffix: '' },
                  { label: 'Skill Gap (Education Mismatch)', name: 'education_mismatch_idx', min: 0, max: 1, step: 0.05, suffix: '' },
                  { label: 'Domain Resilience Score', name: 'resilience_score', min: 0, max: 20, step: 0.5, suffix: '' }
                ].map((input) => (
                  <div key={input.name} className="group">
                    <label className="flex justify-between text-sm font-medium text-gray-400 mb-3 transition-colors group-hover:text-gray-200">
                      <span className="uppercase tracking-wider text-xs">{input.label}</span>
                      <span className="text-[#00f3ff] font-mono text-base bg-[#00f3ff]/10 px-3 py-1 rounded-md border border-[#00f3ff]/20">
                        {input.pre}{input.name === 'annual_salary_usd' ? formData[input.name].toLocaleString() : formData[input.name]}{input.suffix}
                      </span>
                    </label>
                    <input 
                      type="range" 
                      name={input.name} 
                      min={input.min} 
                      max={input.max} 
                      step={input.step} 
                      value={formData[input.name]} 
                      onChange={handleChange} 
                      className="w-full h-1.5 bg-gray-800 rounded-lg appearance-none cursor-pointer outline-none focus:ring-2 focus:ring-[#00f3ff]/50 transition-all [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:bg-[#00f3ff] [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:shadow-[0_0_10px_#00f3ff]" 
                    />
                  </div>
                ))}

                {/* Toggles */}
                <div className="flex gap-8 pt-4 border-t border-white/5">
                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input type="checkbox" name="is_remote_eligible" checked={formData.is_remote_eligible === 1} onChange={handleChange} className="sr-only peer" />
                      <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:bg-[#bc13fe] transition-colors border border-gray-600 peer-checked:border-[#bc13fe]"></div>
                      <div className="absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform peer-checked:translate-x-5 shadow-sm"></div>
                    </div>
                    <span className="text-sm uppercase tracking-wider text-gray-400 group-hover:text-white transition-colors">Remote Eligible</span>
                  </label>

                  <label className="flex items-center gap-3 cursor-pointer group">
                    <div className="relative">
                      <input type="checkbox" name="is_senior" checked={formData.is_senior === 1} onChange={handleChange} className="sr-only peer" />
                      <div className="w-11 h-6 bg-gray-700 rounded-full peer peer-checked:bg-[#00f3ff] transition-colors border border-gray-600 peer-checked:border-[#00f3ff]"></div>
                      <div className="absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform peer-checked:translate-x-5 shadow-sm"></div>
                    </div>
                    <span className="text-sm uppercase tracking-wider text-gray-400 group-hover:text-white transition-colors">Senior Orchestrator</span>
                  </label>
                </div>

                <button 
                  onClick={handleCalculate} 
                  disabled={loading}
                  className="w-full mt-4 py-4 rounded-xl font-bold bg-white text-black hover:bg-gray-200 transition-all duration-300 shadow-[0_0_20px_rgba(255,255,255,0.15)] uppercase tracking-[0.2em] text-sm relative overflow-hidden group"
                >
                  <span className="relative z-10 flex items-center justify-center gap-2">
                    {loading ? <Zap className="animate-spin" size={18} /> : <Zap size={18} />}
                    {loading ? 'Simulating Neural Matrix...' : 'Compute Probability Vector'}
                  </span>
                  <div className="absolute inset-0 bg-gradient-to-r from-[#00f3ff] to-[#bc13fe] opacity-0 group-hover:opacity-20 transition-opacity duration-500"></div>
                </button>
              </div>
            </div>

            {/* RIGHT: Output Gauge (5 cols) */}
            <div className="lg:col-span-5 relative flex flex-col items-center justify-center p-10 border-l border-white/5 bg-black/40 min-h-[400px]">
              
              <AnimatePresence mode="wait">
                {result ? (
                  <motion.div 
                    key="result"
                    initial={{ scale: 0.9, opacity: 0, filter: 'blur(10px)' }}
                    animate={{ scale: 1, opacity: 1, filter: 'blur(0px)' }}
                    exit={{ scale: 0.9, opacity: 0, filter: 'blur(10px)' }}
                    transition={{ duration: 0.5, type: "spring", bounce: 0.4 }}
                    className="flex flex-col items-center justify-center w-full"
                  >
                    {/* Glowing Perimeter Ring */}
                    <div className={`relative mb-10 w-56 h-56 rounded-full flex items-center justify-center ${activeStyle.shadow} transition-shadow duration-700`}>
                      
                      <div className={`absolute inset-0 rounded-full border border-white/10 ${activeStyle.bg} backdrop-blur-3xl animate-pulse-slow`}></div>
                      
                      {/* Animated SVG Gauge */}
                      <svg className="absolute inset-0 w-full h-full -rotate-90 pointer-events-none" viewBox="0 0 100 100">
                         {/* Track */}
                         <circle cx="50" cy="50" r="46" fill="transparent" stroke="rgba(255,255,255,0.05)" strokeWidth="4" />
                         {/* Fill */}
                         <motion.circle 
                            cx="50" cy="50" r="46" fill="transparent" 
                            stroke="currentColor" 
                            strokeWidth="4" 
                            strokeLinecap="round"
                            className={activeStyle.color}
                            strokeDasharray="289.02" 
                            initial={{ strokeDashoffset: 289.02 }}
                            animate={{ strokeDashoffset: 289.02 - (289.02 * result.displacement_probability_pct) / 100 }}
                            transition={{ duration: 1.8, ease: "easeOut", delay: 0.2 }}
                         />
                      </svg>
                      
                      {/* Metric Display */}
                      <div className="relative text-center font-mono">
                        <span className={`text-6xl font-black tracking-tighter ${activeStyle.color} drop-shadow-lg`}>
                          {result.displacement_probability_pct.toFixed(1)}
                        </span>
                        <span className={`text-2xl ${activeStyle.color}`}>%</span>
                        <div className="text-[10px] text-gray-400 uppercase tracking-[0.3em] mt-2">Displacement Probability</div>
                      </div>
                    </div>

                    {/* Threat Analysis Card */}
                    <motion.div 
                       initial={{ y: 20, opacity: 0 }}
                       animate={{ y: 0, opacity: 1 }}
                       transition={{ delay: 0.8, duration: 0.6 }}
                       className={`w-full p-5 rounded-xl border flex flex-col items-center gap-3 ${activeStyle.bg} ${activeStyle.border} backdrop-blur-md`}
                    >
                      <div className={`flex items-center justify-center w-12 h-12 rounded-full bg-black/50 ${activeStyle.color} ${activeStyle.border} border`}>
                        {result.zone === "Red Zone" ? <ShieldAlert size={20} /> : (result.zone === "Green Zone" ? <ShieldCheck size={20} /> : <Activity size={20} />)}
                      </div>
                      <div className="text-center">
                        <div className="text-[10px] text-gray-400 uppercase tracking-widest mb-1">Assessed Threat Level</div>
                        <span className={`font-black text-lg uppercase tracking-wider ${activeStyle.color} text-center leading-tight`}>
                          {result.resilience_category}
                        </span>
                      </div>
                    </motion.div>
                    
                  </motion.div>
                ) : (
                  <motion.div 
                    key="empty"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="flex flex-col items-center justify-center text-gray-500"
                  >
                    <div className="w-32 h-32 rounded-full border border-dashed border-gray-700 flex items-center justify-center mb-6 relative">
                      <div className="absolute inset-0 bg-[#00f3ff]/5 blur-xl rounded-full animate-pulse"></div>
                      <Activity size={32} className="text-gray-600" />
                    </div>
                    <p className="font-mono text-xs uppercase tracking-[0.2em]">Awaiting Telemetry Sync...</p>
                  </motion.div>
                )}
              </AnimatePresence>

            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

export default App;
