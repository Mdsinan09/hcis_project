import React, { useState, useEffect, useRef, useCallback, forwardRef } from 'react';
import { motion, useInView, useAnimation, AnimatePresence, useScroll, useTransform } from 'framer-motion';

// --- Icon Definitions ---

const VideoIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 8-6 4 6 4V8Z"/><path d="M14 12c-2.2 0-4-1.8-4-4V4c0-2.2 1.8-4 4-4s4 1.8 4 4v4c0 2.2-1.8 4-4 4Z" opacity=".3"/><path d="M2 12c-2.2 0-4-1.8-4-4V4c0-2.2 1.8-4 4-4s4 1.8 4 4v4c0 2.2-1.8 4-4 4Z"/></svg>);
const AudioIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v6a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2" opacity=".3"/><line x1="12" x2="12" y1="19" y2="22"/></svg>);
const TextIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17 6H3"/><path d="M21 12H3"/><path d="M17 18H3"/></svg>);
const UploadIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v12"/><path d="m19 9-7-7-7 7"/><path d="M20 18v3a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1v-3"/></svg>);
const AnalyzeIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M19 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><path d="M16 13a4 4 0 0 0-8 0"/><rect width="18" height="3" x="3" y="10" rx="1"/><path d="m15 13-3 3-3-3"/></svg>);
const ResultsIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11V3h-8"/><path d="M22 3 10 15"/><path d="M6 16.5L1.5 12 6 7.5"/><path d="M18 7.5 22.5 12 18 16.5" opacity=".3"/></svg>);
const ShieldCheckIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>);
const ZapIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>);
const LoaderIcon = (props) => (<svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12a9 9 0 1 1-6.219-8.56"/></svg>);

// --- Aurora Background Component ---
const AuroraBackground = () => {
  return (
    <div className="fixed inset-0 -z-20 overflow-hidden">
      {/* Base dark background */}
      <div className="absolute inset-0 bg-gradient-to-br from-gray-950 via-gray-900 to-black"></div>
      
      {/* Aurora effect layers */}
      <motion.div
        className="absolute inset-0 opacity-30"
        animate={{
          background: [
            'radial-gradient(ellipse at 20% 30%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)',
            'radial-gradient(ellipse at 80% 70%, rgba(147, 51, 234, 0.3) 0%, transparent 50%)',
            'radial-gradient(ellipse at 40% 80%, rgba(6, 182, 212, 0.3) 0%, transparent 50%)',
            'radial-gradient(ellipse at 20% 30%, rgba(59, 130, 246, 0.3) 0%, transparent 50%)',
          ],
        }}
        transition={{
          duration: 10,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      
      <motion.div
        className="absolute inset-0 opacity-20"
        animate={{
          background: [
            'radial-gradient(ellipse at 60% 20%, rgba(168, 85, 247, 0.4) 0%, transparent 50%)',
            'radial-gradient(ellipse at 30% 60%, rgba(59, 130, 246, 0.4) 0%, transparent 50%)',
            'radial-gradient(ellipse at 70% 80%, rgba(14, 165, 233, 0.4) 0%, transparent 50%)',
            'radial-gradient(ellipse at 60% 20%, rgba(168, 85, 247, 0.4) 0%, transparent 50%)',
          ],
        }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: "linear"
        }}
      />
      
      {/* Subtle gradient overlays */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-black/30"></div>
    </div>
  );
};

// --- Utility Functions ---

const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key=`;

const fetchWithRetry = async (url, options, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url, options);
      if (response.ok) {
        return response;
      }
      if (response.status === 403) {
        throw new Error(`API access denied (403). Please ensure your API key is correctly configured and authorized.`);
      }
      if (response.status >= 400 && response.status < 500) {
        throw new Error(`API returned client error: ${response.status}`);
      }
      throw new Error(`API returned status ${response.status}. Retrying...`);
    } catch (error) {
      if (i === retries - 1) throw error;
      const delay = Math.pow(2, i) * 1000;
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
};

// --- Component Definitions ---

const containerVariants = {
  hidden: { opacity: 0, y: 50 },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.8,
      ease: "easeOut",
      staggerChildren: 0.1,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6 } },
};

const GlassCard = ({ children, className = '', hoverEffect = false, ...props }) => (
  <motion.div
    className={`
      ${className}
      relative p-6 rounded-3xl border border-gray-700/50 shadow-2xl
      bg-white/5 backdrop-blur-md overflow-hidden
      transition duration-500
      ${hoverEffect ? 'hover:bg-white/10 hover:shadow-gray-800/80' : ''}
    `}
    style={{
      boxShadow: '0 0 30px rgba(0,0,0,0.5)',
      backdropFilter: 'blur(12px) saturate(150%)',
      WebkitBackdropFilter: 'blur(12px) saturate(150%)',
    }}
    {...props}
  >
    {children}
  </motion.div>
);

const GlassButton = ({ children, className = '', large = false, ...props }) => (
  <motion.button
    whileHover={{ y: -3, boxShadow: '0 10px 30px rgba(0, 150, 255, 0.4)' }}
    whileTap={{ y: 0 }}
    className={`
      relative font-medium tracking-wide transition duration-300 ease-out
      rounded-full border border-gray-300/30
      bg-white/10 backdrop-blur-sm
      text-white
      ${large ? 'px-10 py-4 text-xl' : 'px-6 py-3 text-base'}
      ${className}
    `}
    style={{
      textShadow: '0 0 5px rgba(255,255,255,0.8)',
      boxShadow: '0 0 10px rgba(255,255,255,0.2) inset, 0 4px 15px rgba(0,0,0,0.5)',
    }}
    {...props}
  >
    <span className="relative z-10">{children}</span>
  </motion.button>
);

const TaglineCycler = () => {
  const taglines = ["Detect.", "Analyze.", "Verify."];
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % taglines.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const currentTagline = taglines[index];

  return (
    <div className="h-8 md:h-10 overflow-hidden">
      <AnimatePresence mode="wait">
        <motion.p
          key={currentTagline}
          initial={{ y: "100%", opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: "-100%", opacity: 0 }}
          transition={{ duration: 0.5, ease: "easeInOut" }}
          className="text-lg md:text-xl font-light text-blue-300 tracking-wider"
        >
          {currentTagline}
        </motion.p>
      </AnimatePresence>
    </div>
  );
};

const AnimatedCounter = ({ endValue, title, subtitle }) => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, amount: 0.5 });
  const [count, setCount] = useState(0);
  const controls = useAnimation();

  useEffect(() => {
    if (inView) {
      controls.start({
        count: endValue,
        transition: { duration: 1.5, ease: "easeOut" },
      });
    }
  }, [inView, endValue, controls]);

  const progress = (count / endValue) * 100;

  return (
    <motion.div
      ref={ref}
      className="text-center p-4"
      initial="hidden"
      animate={inView ? "visible" : "hidden"}
      variants={itemVariants}
    >
      <motion.div
        className="text-5xl lg:text-7xl font-bold mb-2 text-white"
        animate={controls}
        onUpdate={latest => setCount(Math.round(latest.count))}
      >
        <p>{count}{title.includes('%') ? '%' : ''}</p>
      </motion.div>
      <p className="text-sm font-medium text-gray-400 uppercase tracking-widest">{title}</p>
      <div className="mt-4 h-1 w-full bg-gray-700 rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-blue-500 shadow-blue-500/50"
          initial={{ width: '0%' }}
          animate={{ width: inView ? `${progress}%` : '0%' }}
          transition={{ duration: 1.5, ease: "easeOut" }}
          style={{ boxShadow: '0 0 10px rgba(59, 130, 246, 0.8)' }}
        />
      </div>
    </motion.div>
  );
};

const SectionWrapper = forwardRef(({ children, id, className = '', onMouseMove, ...props }, ref) => {
  const localRef = useRef(null);
  const targetRef = ref || localRef;
  const inView = useInView(targetRef, { once: true, amount: 0.1 });

  return (
    <motion.section
      id={id}
      ref={targetRef}
      className={`relative py-24 md:py-36 min-h-screen flex items-center justify-center ${className}`}
      initial="hidden"
      animate={inView ? "visible" : "hidden"}
      variants={containerVariants}
      onMouseMove={onMouseMove}
      {...props}
    >
      {children}
    </motion.section>
  );
});

const TextVerificationTool = () => {
  const [inputText, setInputText] = useState('The stock market is guaranteed to rise by 50% next quarter due to a secret new technology launch by a major firm.');
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const riskColorMap = {
    Low: 'text-green-400 border-green-500 bg-green-900/20',
    Medium: 'text-yellow-400 border-yellow-500 bg-yellow-900/20',
    High: 'text-red-400 border-red-500 bg-red-900/20',
    Error: 'text-red-400 border-red-500 bg-red-900/20',
  };

  const analyzeText = async () => {
    if (!inputText || inputText.length < 20) {
        setResult({
            score: 0,
            risk: "Error",
            summary: "Please provide content longer than 20 characters for a meaningful analysis."
        });
        return;
    }

    setIsLoading(true);
    setResult(null);

    const systemPrompt = "You are the HCIS Text Integrity Analyst, powered by Google's Gemini. Your task is to analyze the provided text and determine its overall integrity. Specifically, evaluate exaggeration, unsubstantiated claims, biased language, and signs of AI-generated content. You must return ONLY a JSON object formatted according to the responseSchema.";
    const userQuery = `Analyze the following text for content integrity: "${inputText}"`;

    const payload = {
        contents: [{ parts: [{ text: userQuery }] }],
        systemInstruction: { parts: [{ text: systemPrompt }] },
        generationConfig: {
            responseMimeType: "application/json",
            responseSchema: {
                type: "OBJECT",
                properties: {
                    score: { 
                        type: "INTEGER", 
                        description: "An integrity confidence score from 1 (lowest confidence/most fake) to 100 (highest confidence/most factual)." 
                    },
                    risk: { 
                        type: "STRING", 
                        enum: ["Low", "Medium", "High"],
                        description: "A summary risk assessment based on the score (Low: 75-100, Medium: 40-74, High: 1-39)."
                    },
                    summary: { 
                        type: "STRING", 
                        description: "A concise, professional summary (max 100 words) detailing the key integrity concerns." 
                    }
                },
                required: ["score", "risk", "summary"]
            }
        }
    };

    try {
        const response = await fetchWithRetry(GEMINI_API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        
        const jsonText = data.candidates?.[0]?.content?.parts?.[0]?.text;
        
        if (!jsonText) {
            console.error("Gemini API Error: No content returned in response structure.", data);
            setResult({ score: 0, risk: "Error", summary: "API returned empty content. Network or content policy error. Check console." });
            return;
        }

        const parsedResult = JSON.parse(jsonText);
        setResult(parsedResult);

    } catch (error) {
        console.error("Gemini API Error:", error);
        setResult({
            score: 0,
            risk: "Error",
            summary: `Analysis failed: ${error.message}. Please check your network connection or try again.`
        });
    } finally {
        setIsLoading(false);
    }
  };

  const riskClass = result?.risk ? riskColorMap[result.risk] : 'text-gray-400 border-gray-500 bg-gray-900/20';

  return (
    <GlassCard className="w-full max-w-4xl mx-auto p-8 border-blue-500/50">
      <h3 className="text-3xl font-semibold mb-6 flex items-center">
        <ZapIcon className="w-6 h-6 mr-3 text-yellow-400" />
        Live Text Integrity Check (Powered by Gemini)
      </h3>
      
      <div className="space-y-4">
        <motion.textarea
          className="w-full min-h-[150px] p-4 text-gray-200 bg-white/5 border border-gray-600/50 rounded-lg backdrop-blur-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition duration-300 resize-none"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onFocus={(e) => {
            if (e.target.value === 'The stock market is guaranteed to rise by 50% next quarter due to a secret new technology launch by a major firm.') {
              setInputText('');
            }
          }}
          onBlur={(e) => {
            if (e.target.value.trim() === '') {
              setInputText('The stock market is guaranteed to rise by 50% next quarter due to a secret new technology launch by a major firm.');
            }
          }}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
        />

        <GlassButton large onClick={analyzeText} disabled={isLoading} className="w-full bg-blue-600/20 border-blue-400/50">
          {isLoading ? (
            <span className="flex items-center justify-center">
              <LoaderIcon className="w-5 h-5 mr-2 animate-spin" />
              Analyzing Content...
            </span>
          ) : (
            'Run HCIS Analysis'
          )}
        </GlassButton>
      </div>

      <motion.div
        className="mt-8 p-0 pt-6"
        initial={{ opacity: 0, height: 0 }}
        animate={{ opacity: result ? 1 : 0, height: result ? 'auto' : 0 }}
        transition={{ duration: 0.5 }}
      >
        <h4 className="text-xl font-semibold text-blue-300 mb-4">Analysis Report:</h4>
        
        {result && (
          <GlassCard className={`p-6 border-2 transition duration-500 ${riskClass}`}>
            
            <div className="flex justify-between items-center mb-4 pb-4 border-b border-gray-700/50">
                <div className="text-left">
                    <p className="text-sm uppercase tracking-widest text-gray-400">Integrity Score</p>
                    <p className={`text-5xl font-extrabold ${riskClass}`}>{result.score}<span className="text-lg">%</span></p>
                </div>

                <div className="text-right">
                    <p className="text-sm uppercase tracking-widest text-gray-400">Risk Assessment</p>
                    <p className={`text-5xl font-extrabold ${riskClass} transition duration-500`}>
                        {result.risk}
                    </p>
                </div>
            </div>
            
            <div className="text-gray-300">
                <p className="font-semibold mb-2 text-white">Analysis Summary:</p>
                <p className="text-sm italic text-gray-400">
                    {result.summary}
                </p>
                {result.score < 40 && (
                    <motion.p 
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ type: "spring", stiffness: 300 }}
                        className="mt-4 text-center text-red-400 font-bold text-lg p-2 border border-red-500 rounded-lg"
                    >
                        ALERT: Potential Misinformation Detected. High Risk.
                    </motion.p>
                )}
            </div>
          </GlassCard>
        )}
      </motion.div>
    </GlassCard>
  );
};

// --- Main App Component ---

const features = [
  { name: "Deepfake Detection", desc: "Identifies synthetic manipulation in media streams." },
  { name: "Source Attribution", desc: "Traces content origins back to verified endpoints." },
  { name: "Sentiment Analysis", desc: "Evaluates the emotional tone of text input." },
  { name: "Real-time Scoring", desc: "Provides instantaneous integrity risk scores." },
  { name: "Evasion Resistance", desc: "Continuously trained against adversarial attacks." },
  { name: "API Integration", desc: "Seamless integration into existing content platforms." },
];

const stats = [
  { endValue: 6, title: "AI Components", subtitle: "Core Models" },
  { endValue: 9, title: "API Endpoints", subtitle: "Access Points" },
  { endValue: 99.8, title: "Accuracy %", subtitle: "Verification Score" },
];

const App = () => {
  const heroRef = useRef(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });

  const handleMouseMove = useCallback((event) => {
    if (heroRef.current) {
      const rect = heroRef.current.getBoundingClientRect();
      setMousePosition({
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      });
    }
  }, []);

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
  };
  
  const redirectToDetector = () => {
      // Replace with your actual frontend webapp URL
      const frontendUrl = "YOUR_FRONTEND_WEBAPP_URL_HERE"; 
      if (frontendUrl.includes('YOUR_FRONTEND_WEBAPP_URL_HERE')) {
          console.log("Placeholder URL: Update with your actual frontend URL");
          window.location.href = "https://your-frontend-app.com";
      } else {
          window.location.href = frontendUrl;
      }
  };

  const { scrollYProgress } = useScroll();
  const scaleImage = useTransform(scrollYProgress, [0, 0.5], [1, 1.05]);
  const yImage = useTransform(scrollYProgress, [0, 0.5], ['0%', '5%']);

  return (
    <div className="min-h-screen bg-[#0A0A0A] font-inter text-white overflow-x-hidden relative">
      {/* Aurora Background */}
      <AuroraBackground />

      {/* Hero Section Mouse-Tracking Glow */}
      <motion.div
        className="pointer-events-none absolute -z-10 rounded-full bg-blue-500/30 blur-3xl opacity-0 md:opacity-100"
        style={{
          width: 300,
          height: 300,
          left: mousePosition.x - 150,
          top: mousePosition.y - 150,
          transition: 'transform 0.1s ease-out, opacity 0.5s ease-out'
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.3 }}
        transition={{ duration: 1 }}
      />

      {/* Sticky Header Navigation */}
      <motion.nav
        initial={{ y: -100, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ type: "spring", stiffness: 100, delay: 0.3 }}
        className="fixed top-0 left-0 right-0 z-50 p-4"
      >
        <div className="max-w-7xl mx-auto flex justify-between items-center h-16">
          <div className="text-xl md:text-2xl font-bold tracking-widest text-white/90">HCIS</div>
          
          <GlassCard className="hidden md:flex p-2 space-x-4 border-gray-600/50">
            {['About', 'How It Works', 'Features', 'Detection'].map((item) => (
              <a
                key={item}
                onClick={() => scrollTo(item.toLowerCase().replace(/\s/g, ''))}
                className="text-sm font-medium text-gray-300 hover:text-white transition duration-300 cursor-pointer px-3 py-1 rounded-full"
              >
                {item === 'Detection' ? 'Gemini Detection' : item}
              </a>
            ))}
          </GlassCard>

          <GlassButton onClick={() => console.log('Action: Redirecting to Sales Contact Form')} className="hidden md:block">Contact Sales</GlassButton>
          
          <div className="md:hidden">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16m-7 6h7"></path></svg>
          </div>
        </div>
      </motion.nav>

      {/* ------------------- 1. HERO SECTION ------------------- */}
      <SectionWrapper id="hero" className="min-h-screen pt-24 text-left bg-transparent" onMouseMove={handleMouseMove} ref={heroRef}>
        <div className="max-w-7xl mx-auto px-4 grid md:grid-cols-2 items-center gap-12">
          {/* Left: Text Content */}
          <div>
            <motion.h1
              initial={{ opacity: 0, x: -50 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1, ease: "easeOut" }}
              className="text-5xl md:text-7xl lg:text-8xl font-extrabold tracking-tighter leading-tight text-white mb-6"
              style={{ textShadow: '0 0 20px rgba(0, 150, 255, 0.5)' }}
            >
              Multi-Modal <br /> AI Detection & Verification System
            </motion.h1>

            <motion.h2
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 1, delay: 0.5 }}
              className="text-2xl md:text-3xl font-light text-gray-300 mb-8"
            >
              A Holistic Content Verification System
            </motion.h2>

            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.5, delay: 1 }}
              className="mb-12"
            >
              <TaglineCycler />
            </motion.div>

            <GlassButton large onClick={redirectToDetector}>
              Start Now
            </GlassButton>
          </div>

          {/* Right: Circuit Brain Image with Parallax */}
          <motion.div
            style={{ y: yImage, scale: scaleImage }}
            className="relative flex justify-center items-center w-full h-96 md:h-[600px] overflow-hidden rounded-3xl"
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 1, delay: 0.7, ease: "easeOut" }}
          >
            <img
              src="f987f99970bcb46cbe78b4b6e91da6d2.jpg"
              alt="AI Brain Circuit"
              className="absolute inset-0 w-full h-full object-contain p-8"
              onError={(e) => { 
                e.target.onerror = null; 
                e.target.src="https://placehold.co/800x800/1a1a2e/ffffff?text=AI+Brain+Circuit" 
              }}
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/40 via-transparent to-transparent rounded-3xl"></div>
          </motion.div>
        </div>
      </SectionWrapper>

      {/* ------------------- 2. ABOUT US / WHAT WE DO ------------------- */}
      <SectionWrapper id="about" className="pt-24 md:pt-36 bg-transparent">
        <div className="max-w-7xl mx-auto px-4">
          <motion.h2 variants={itemVariants} className="text-4xl md:text-5xl font-bold text-center mb-4">
            About HCIS: Integrity in the Digital Age
          </motion.h2>
          <motion.p variants={itemVariants} className="text-xl text-gray-400 text-center mb-16 max-w-3xl mx-auto">
            Founded on the principle of verifiable truth, HCIS provides a robust defense against misinformation.
          </motion.p>

          <motion.div variants={containerVariants} className="grid md:grid-cols-2 gap-12 mb-20">
            <motion.div variants={itemVariants} className="space-y-6">
              <h3 className="text-3xl font-semibold text-white">Our Mission</h3>
              <p className="text-gray-400 leading-relaxed text-lg">
                In an era saturated with digitally manipulated content, HCIS stands as a beacon of trust. Our mission is to empower individuals and organizations with advanced AI tools to detect and verify the authenticity of multi-modal content, fostering a more credible digital landscape. We believe that clarity and truth are paramount for informed decision-making and secure communication.
              </p>
              <GlassButton onClick={() => scrollTo('features')} className="mt-4">Learn More About Us</GlassButton> 
            </motion.div>
            <motion.div variants={itemVariants} className="space-y-6">
              <h3 className="text-3xl font-semibold text-white">The HCIS Advantage</h3>
              <p className="text-gray-400 leading-relaxed text-lg">
                Leveraging state-of-the-art machine learning, forensic analysis, and deep neural networks, HCIS offers unparalleled accuracy and speed. Unlike conventional systems, our multi-modal approach scrutinizes video, audio, and text simultaneously, ensuring comprehensive coverage and identifying subtle discrepancies often missed by single-domain detectors.
              </p>
              <GlassButton onClick={() => scrollTo('howitworks')} className="mt-4">Explore Our Technology</GlassButton> 
            </motion.div>
          </motion.div>

          <motion.h3 variants={itemVariants} className="text-3xl md:text-4xl font-bold text-center mb-10">
            Our Core Verification Pillars
          </motion.h3>
          <motion.div variants={containerVariants} className="grid md:grid-cols-3 gap-8">
            {[
              { icon: VideoIcon, title: "Video Authenticity", text: "Pixel-level analysis detects deepfakes, splicing, and manipulation in video streams." },
              { icon: AudioIcon, title: "Audio Verification", text: "Checks voice cloning, synthesis, and acoustic anomalies for synthetic audio content." },
              { icon: TextIcon, title: "Text Fact-Checking", text: "Cross-references claims against global knowledge bases to score textual integrity." },
            ].map((card, index) => (
              <GlassCard key={index} hoverEffect variants={itemVariants} className="flex flex-col items-start space-y-4">
                <card.icon className="w-10 h-10 text-blue-400" strokeWidth={1.5} />
                <h3 className="text-2xl font-semibold">{card.title}</h3>
                <p className="text-gray-400">{card.text}</p>
              </GlassCard>
            ))}
          </motion.div>
        </div>
      </SectionWrapper>

      {/* ------------------- 3. HOW IT WORKS ------------------- */}
      <SectionWrapper id="howitworks" className="pt-24 md:pt-36 relative overflow-hidden bg-transparent">
        <div className="absolute inset-0 -z-10 opacity-10">
          <svg className="w-full h-full" viewBox="0 0 1000 1000" preserveAspectRatio="xMidYMid slice">
            <motion.path
              d="M0 500 C 150 400, 300 600, 500 500 S 850 400, 1000 500"
              stroke="#60a5fa" fill="none" strokeWidth="0.5"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 1, transition: { duration: 2, ease: "easeOut", delay: 0.5 } }}
              viewport={{ once: true }}
            />
            <motion.path
              d="M0 400 C 180 300, 320 550, 500 450 S 820 350, 1000 450"
              stroke="#3b82f6" fill="none" strokeWidth="0.5"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 1, transition: { duration: 2, ease: "easeOut", delay: 0.7 } }}
              viewport={{ once: true }}
            />
            <motion.path
              d="M0 600 C 120 700, 280 450, 500 550 S 880 700, 1000 600"
              stroke="#93c5fd" fill="none" strokeWidth="0.5"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 1, transition: { duration: 2, ease: "easeOut", delay: 0.9 } }}
              viewport={{ once: true }}
            />
          </svg>
        </div>

        <div className="max-w-7xl mx-auto px-4 relative z-10">
          <motion.h2 variants={itemVariants} className="text-4xl md:text-5xl font-bold text-center mb-16">
            The HCIS Integrity Loop
          </motion.h2>

          <motion.div variants={containerVariants} className="relative flex flex-col md:flex-row justify-between items-center">
            <div className="hidden md:block absolute top-1/2 left-0 right-0 h-1 bg-gray-700/50 transform -translate-y-1/2 mx-16">
              <motion.div
                initial={{ width: 0 }}
                whileInView={{ width: '100%', transition: { duration: 1.5, delay: 0.5 } }}
                viewport={{ once: true, amount: 0.5 }}
                className="h-full bg-blue-500 shadow-blue-500/50"
              />
            </div>

            {[
              { step: 1, title: "Upload", icon: UploadIcon, desc: "Securely submit content via API or portal." },
              { step: 2, title: "Analyze", icon: AnalyzeIcon, desc: "Multi-modal AI models scan for anomalies." },
              { step: 3, title: "Results", icon: ResultsIcon, desc: "Receive a definitive, auditable integrity report." },
            ].map((item, index) => (
              <GlassCard
                key={index}
                hoverEffect
                variants={itemVariants}
                className="w-full md:w-[30%] min-h-[200px] text-center flex flex-col items-center justify-center p-8 mb-10 md:mb-0 relative z-10"
              >
                <div className="p-3 mb-4 rounded-full bg-blue-500/20 border border-blue-500/50">
                  <item.icon className="w-8 h-8 text-blue-400" strokeWidth={2} />
                </div>
                <h3 className="text-xl font-semibold mb-2 flex items-center justify-center">
                  <span className="text-blue-400 mr-2">Step {item.step}:</span> {item.title}
                </h3>
                <p className="text-gray-400 text-sm">{item.desc}</p>
              </GlassCard>
            ))}
          </motion.div>
        </div>
      </SectionWrapper>

      {/* ------------------- 5. FEATURES SECTION ------------------- */}
      <SectionWrapper id="features" className="pt-24 md:pt-36 bg-transparent min-h-0">
        <div className="max-w-7xl mx-auto px-4">
          <motion.h2 variants={itemVariants} className="text-4xl md:text-5xl font-bold text-center mb-4">
            Core Capabilities
          </motion.h2>
          <motion.p variants={itemVariants} className="text-xl text-gray-400 text-center mb-16 max-w-3xl mx-auto">
            A comprehensive suite of tools built on robust, cutting-edge AI architecture.
          </motion.p>

          <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {features.map((feature, index) => (
              <GlassCard
                key={index}
                hoverEffect
                variants={itemVariants}
                className="flex flex-col space-y-2 p-5 text-left"
              >
                <div className="flex items-center space-x-3">
                  <ShieldCheckIcon className="w-5 h-5 text-green-400" />
                  <h4 className="text-lg font-semibold">{feature.name}</h4>
                </div>
                <p className="text-gray-400 text-sm">{feature.desc}</p>
              </GlassCard>
            ))}
          </motion.div>
        </div>
      </SectionWrapper>

      {/* ------------------- 6. STATS / HIGHLIGHTS ------------------- */}
      <SectionWrapper id="stats" className="pt-24 md:pt-36 min-h-0">
        <div className="max-w-7xl mx-auto px-4">
          <motion.h2 variants={itemVariants} className="text-4xl md:text-5xl font-bold text-center mb-16">
            Unrivaled Performance
          </motion.h2>

          <motion.div variants={containerVariants} className="grid grid-cols-1 md:grid-cols-3 gap-12 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <AnimatedCounter key={index} {...stat} />
            ))}
          </motion.div>
        </div>
      </SectionWrapper>

      {/* ------------------- 7. CALL TO ACTION (CTA) ------------------- */}
      <SectionWrapper id="contact" className="pt-24 md:pt-36 pb-36 min-h-0">
        <div className="max-w-4xl mx-auto px-4 w-full">
          <GlassCard
            variants={itemVariants}
            className="text-center p-12 md:p-16 border-blue-500/50"
            style={{ boxShadow: '0 0 40px rgba(59, 130, 246, 0.4)' }}
          >
            <h2 className="text-3xl md:text-4xl font-light mb-6">
              Ready to <span className="font-semibold text-blue-300">Verify Content?</span>
            </h2>
            <p className="text-lg text-gray-400 mb-8 max-w-2xl mx-auto">
              Integrate HCIS today and begin building trust in your digital ecosystem.
            </p>
            <GlassButton large onClick={redirectToDetector} className="bg-blue-600/20 border-blue-400/50">
              Start Now
            </GlassButton>
          </GlassCard>
        </div>
      </SectionWrapper>

      {/* Footer */}
      <div className="py-6 border-t border-gray-800 text-center text-xs text-gray-600">
        &copy; {new Date().getFullYear()} HCIS - Human Content Integrity System. All Rights Reserved.
      </div>
    </div>
  );
};

export default App;