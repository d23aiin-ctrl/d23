"use client"

import { useState, useRef, useEffect, createContext, useContext } from "react"
import Image from "next/image"
import Link from "next/link"
import { motion, useScroll, useTransform, useInView, useMotionValue, useSpring, AnimatePresence } from "framer-motion"

const useHydrated = () => {
  const [hydrated, setHydrated] = useState(false)
  useEffect(() => {
    setHydrated(true)
  }, [])
  return hydrated
}

import { Sparkles, Mic, ShieldCheck, Sticker, Gamepad2, MessageCircle, ChevronDown, ArrowRight, Play, Languages, ImageIcon, Zap, Globe, Check, X as XIcon, Lock, Star, Phone } from "lucide-react"
import { cn } from "@/lib/utils"
import { LanguageProvider, useLanguage, useTranslations, languages as supportedLanguages } from "@/lib/i18n/LanguageContext"
import { LanguageSwitcher, LanguageBar } from "@/components/LanguageSwitcher"

// ============== LANDING CONTENT CONTEXT ==============
interface LandingContent {
  hero: {
    title: string;
    subtitle: string;
    rotatingWords: string[];
    description: string;
    ctaPrimary: string;
    ctaSecondary: string;
    whatsappLink: string;
  };
  stats: Array<{ value: string; label: string; icon: string }>;
  languages: Array<{ name: string; code: string; english: string }>;
  meta: { title: string; description: string };
}

const defaultContent: LandingContent = {
  hero: {
    title: "Need an answer?",
    subtitle: "just",
    rotatingWords: ["पूछो", "કહો", "ಕೇಳಿ", "అడుగు", "D23"],
    description: "Your AI assistant that speaks your language. Get instant answers in 11+ languages — Hindi, Tamil, Telugu & more.",
    ctaPrimary: "Start on WhatsApp",
    ctaSecondary: "Try Web Chat",
    whatsappLink: "https://wa.me/919934438606",
  },
  stats: [
    { value: "5000+", label: "Active Users", icon: "👥" },
    { value: "11+", label: "Languages", icon: "🌐" },
    { value: "24/7", label: "Available", icon: "⚡" },
    { value: "<2s", label: "Response", icon: "🚀" },
  ],
  languages: [
    { name: "हिंदी", code: "hi", english: "Hindi" },
    { name: "தமிழ்", code: "ta", english: "Tamil" },
    { name: "తెలుగు", code: "te", english: "Telugu" },
    { name: "ಕನ್ನಡ", code: "kn", english: "Kannada" },
    { name: "മലയാളം", code: "ml", english: "Malayalam" },
    { name: "ગુજરાતી", code: "gu", english: "Gujarati" },
    { name: "मराठी", code: "mr", english: "Marathi" },
    { name: "বাংলা", code: "bn", english: "Bengali" },
    { name: "ਪੰਜਾਬੀ", code: "pa", english: "Punjabi" },
    { name: "ଓଡ଼ିଆ", code: "or", english: "Odia" },
    { name: "English", code: "en", english: "English" },
  ],
  meta: {
    title: "D23 AI | Your Multilingual WhatsApp AI Assistant",
    description: "Get instant answers in Hindi, Tamil, Telugu & 11+ languages worldwide",
  },
};

const LandingContentContext = createContext<LandingContent>(defaultContent);
const useLandingContent = () => useContext(LandingContentContext);

// ============== DATA ==============
const rotatingWords = defaultContent.hero.rotatingWords;
const marqueeLanguages = defaultContent.languages;

const multilingualMessages = [
  { lang: "Hindi", langCode: "hi", user: "मुझे आज का मौसम बताओ", bot: "दिल्ली में आज 32°C है, धूप और साफ आसमान। शाम को हल्की बारिश की संभावना है।", flag: "🇮🇳" },
  { lang: "Tamil", langCode: "ta", user: "இன்றைய செய்தி என்ன?", bot: "இந்தியா vs ஆஸ்திரேலியா கிரிக்கெட் போட்டியில் இந்தியா 7 விக்கெட் வித்தியாசத்தில் வெற்றி பெற்றது!", flag: "🇮🇳" },
  { lang: "Telugu", langCode: "te", user: "నాకు ఒక జోక్ చెప్పు", bot: "టీచర్: నువ్వు హోమ్‌వర్క్ ఎందుకు చేయలేదు? స్టూడెంట్: మా ఇంట్లో లైట్ పోయింది సార్! 😄", flag: "🇮🇳" },
  { lang: "Bengali", langCode: "bn", user: "একটি রেসিপি বলুন", bot: "মাছের ঝোল: সরিষার তেলে মাছ ভাজুন, পেঁয়াজ-রসুন বাটা দিন, হলুদ-লংকা মেশান।", flag: "🇮🇳" },
  { lang: "Marathi", langCode: "mr", user: "आज कोणता सण आहे?", bot: "आज गणेश चतुर्थी आहे! गणपती बाप्पा मोरया! 🙏", flag: "🇮🇳" },
  { lang: "Gujarati", langCode: "gu", user: "મને એક વાર્તા કહો", bot: "એક સમયે એક ડાહ્યો કાગડો હતો. તે પાણી માટે ઘડામાં કાંકરા નાખીને પાણી ઉપર લાવ્યો! 🪨", flag: "🇮🇳" },
  { lang: "Kannada", langCode: "kn", user: "ಇಂದು ಯಾವ ದಿನ?", bot: "ಇಂದು ಶುಕ್ರವಾರ, ಡಿಸೆಂಬರ್ 18, 2025. ಶುಭ ದಿನ! ✨", flag: "🇮🇳" },
  { lang: "Malayalam", langCode: "ml", user: "ഒരു ചിത്രം ഉണ്ടാക്കൂ", bot: "ശരി! ഞാൻ നിങ്ങൾക്കായി ഒരു മനോഹരമായ കേരള ബാക്ക്‌വാട്ടർ ചിത്രം ഉണ്ടാക്കുന്നു... 🎨", flag: "🇮🇳" },
  { lang: "Punjabi", langCode: "pa", user: "ਮੈਨੂੰ ਗਾਣਾ ਸੁਣਾਓ", bot: "ਬੱਲੇ ਬੱਲੇ! ਤੁਸੀਂ ਕਿਹੜਾ ਗਾਣਾ ਸੁਣਨਾ ਚਾਹੁੰਦੇ ਹੋ? 🎵", flag: "🇮🇳" },
  { lang: "Odia", langCode: "or", user: "ଆଜି ପାଣିପାଗ କେମିତି?", bot: "ଭୁବନେଶ୍ୱରରେ ଆଜି 28°C, ଆଂଶିକ ମେଘୁଆ ଆକାଶ। ☀️", flag: "🇮🇳" },
  { lang: "English", langCode: "en", user: "Tell me a fact", bot: "Did you know? There are over 7,000 languages spoken worldwide, and D23 AI supports 11+ of them! 🌍", flag: "🌐" },
]

// ============== LANGUAGE MARQUEE ==============
function LanguageMarquee() {
  const content = useLandingContent();
  const languages = content.languages;

  return (
    <div className="relative w-full overflow-hidden py-8 bg-gradient-to-r from-violet-50/30 via-neutral-50/80 to-indigo-50/30 backdrop-blur-sm border-y border-neutral-100">
      <div className="absolute left-0 top-0 bottom-0 w-32 bg-gradient-to-r from-white to-transparent z-10" />
      <div className="absolute right-0 top-0 bottom-0 w-32 bg-gradient-to-l from-white to-transparent z-10" />
      <div className="flex animate-marquee whitespace-nowrap">
        {[...languages, ...languages, ...languages].map((lang, i) => (
          <span key={`${lang.code}-${i}`} className="mx-8 md:mx-12 text-2xl md:text-4xl font-medium text-neutral-400 hover:text-neutral-900 transition-colors cursor-default select-none">
            {lang.name}
          </span>
        ))}
      </div>
      <div className="flex animate-marquee-reverse whitespace-nowrap mt-4">
        {[...languages, ...languages, ...languages].reverse().map((lang, i) => (
          <span key={`reverse-${lang.code}-${i}`} className="mx-8 md:mx-12 text-xl md:text-3xl font-medium text-neutral-300 hover:text-neutral-600 transition-colors cursor-default select-none">
            {lang.english}
          </span>
        ))}
      </div>
    </div>
  )
}

// ============== MAGNETIC BUTTON ==============
function MagneticButton({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("relative transition-transform duration-200 hover:scale-105", className)}>
      {children}
    </div>
  )
}

// ============== 3D TILT CARD ==============
function TiltCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const x = useMotionValue(0)
  const y = useMotionValue(0)
  const rotateX = useSpring(useTransform(y, [-0.5, 0.5], [10, -10]), { stiffness: 300, damping: 30 })
  const rotateY = useSpring(useTransform(x, [-0.5, 0.5], [-10, 10]), { stiffness: 300, damping: 30 })

  const handleMouse = (e: React.MouseEvent) => {
    if (!ref.current) return
    const rect = ref.current.getBoundingClientRect()
    x.set((e.clientX - rect.left) / rect.width - 0.5)
    y.set((e.clientY - rect.top) / rect.height - 0.5)
  }

  const reset = () => { x.set(0); y.set(0) }

  return (
    <motion.div ref={ref} onMouseMove={handleMouse} onMouseLeave={reset} style={{ rotateX, rotateY, transformStyle: "preserve-3d", position: "relative" }} className={className}>
      {children}
    </motion.div>
  )
}

// ============== TEXT REVEAL ==============
function TextReveal({ children, className = "" }: { children: string; className?: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  return (
    <span ref={ref} className={cn("inline-block overflow-hidden", className)}>
      <motion.span initial={{ y: "100%" }} animate={isInView ? { y: 0 } : {}} transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }} className="inline-block">
        {children}
      </motion.span>
    </span>
  )
}

// ============== STAGGER CONTAINER ==============
function StaggerContainer({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-50px" })

  return (
    <motion.div ref={ref} initial="hidden" animate={isInView ? "visible" : "hidden"} variants={{ visible: { transition: { staggerChildren: 0.1 } } }} className={className}>
      {children}
    </motion.div>
  )
}

function StaggerItem({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <motion.div variants={{ hidden: { opacity: 0, y: 30 }, visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.22, 1, 0.36, 1] } } }} className={className}>
      {children}
    </motion.div>
  )
}

// ============== GRADIENT TEXT ==============
function GradientText({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn("bg-gradient-to-r from-violet-600 via-indigo-500 to-blue-500 bg-clip-text text-transparent", className)}>
      {children}
    </span>
  )
}

// ============== ROTATING WORD ==============
function RotatingWord({ words }: { words: string[] }) {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => setIndex((i) => (i + 1) % words.length), 2500)
    return () => clearInterval(interval)
  }, [words.length])

  return (
    <AnimatePresence mode="wait">
      <motion.span key={index} initial={{ opacity: 0, y: 30, rotateX: -90 }} animate={{ opacity: 1, y: 0, rotateX: 0 }} exit={{ opacity: 0, y: -30, rotateX: 90 }} transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }} className="inline-block">
        <GradientText>{words[index]}</GradientText>
      </motion.span>
    </AnimatePresence>
  )
}

// ============== GRADIENT BORDER CARD (legacy) ==============
function GradientBorderCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn("relative p-[1px] rounded-2xl overflow-hidden group", className)}>
      <div className="absolute inset-0 bg-gradient-to-r from-violet-500 to-indigo-500 opacity-20 group-hover:opacity-40 transition-opacity duration-300" style={{ filter: "blur(8px)" }} />
      <div className="absolute inset-0 bg-gradient-to-r from-violet-500 to-indigo-500 rounded-2xl" />
      <div className="relative bg-white rounded-2xl">{children}</div>
    </div>
  )
}

// ============== PREMIUM CARD (Stripe-style layered shadows) ==============
function PremiumCard({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={cn(
      "bg-white rounded-2xl border border-neutral-200/80 transition-all duration-300",
      "shadow-[0_1px_3px_rgba(0,0,0,0.04),0_6px_16px_rgba(0,0,0,0.06)]",
      "hover:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_12px_32px_rgba(0,0,0,0.08)]",
      "hover:border-neutral-300/80",
      className
    )}>
      {children}
    </div>
  )
}

// ============== SECTION DIVIDER ==============
function SectionDivider() {
  return <div className="h-px bg-gradient-to-r from-transparent via-violet-200/50 to-transparent" />
}

// ============== ANIMATED COUNTER ==============
function AnimatedCounter({ value, suffix = "" }: { value: number; suffix?: string }) {
  const [count, setCount] = useState(0)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true })

  useEffect(() => {
    if (isInView) {
      const duration = 2000
      const steps = 60
      const increment = value / steps
      let current = 0
      const timer = setInterval(() => {
        current += increment
        if (current >= value) {
          setCount(value)
          clearInterval(timer)
        } else {
          setCount(Math.floor(current))
        }
      }, duration / steps)
      return () => clearInterval(timer)
    }
  }, [isInView, value])

  return <span ref={ref}>{count}{suffix}</span>
}

// ============== PHONE CHAT MESSAGES DATA ==============
const phoneChatMessages = [
  { type: "user", lang: "hi", text: "मुझे आज का मौसम बताओ 🌤️" },
  { type: "bot", lang: "hi", content: (
    <div>
      <p className="text-xs text-neutral-500 mb-1">🇮🇳 दिल्ली</p>
      <p>🌡️ <span className="font-semibold">32°C</span> • साफ आसमान</p>
      <p className="text-neutral-500 text-xs mt-1">💧 नमी: 45% | 💨 हवा: 12 km/h</p>
    </div>
  )},
  { type: "user", lang: "ta", text: "இன்றைய ராசிபலன் ♌" },
  { type: "bot", lang: "ta", content: (
    <div>
      <p className="text-xs text-violet-400 mb-1">♌ சிம்மம் ராசி</p>
      <p className="text-xs">இன்று காலை 9-11 மணி சிறந்த நேரம். புதிய வாய்ப்புகள் வரும். ⭐⭐⭐⭐</p>
    </div>
  )},
  { type: "user", lang: "en", text: "Generate a sunset image 🎨" },
  { type: "bot", lang: "en", content: (
    <div>
      <div className="w-full h-20 rounded-lg mb-2 overflow-hidden bg-gradient-to-br from-orange-400 via-pink-500 to-violet-600 flex items-center justify-center">
        <span className="text-2xl">🌅</span>
      </div>
      <p className="text-xs text-neutral-500">Here&apos;s your AI-generated image! 🌅</p>
    </div>
  )},
  { type: "user", lang: "te", text: "స్టికర్ చేయి 🎭" },
  { type: "bot", lang: "te", content: (
    <div>
      <div className="w-16 h-16 rounded-xl mb-1 bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center">
        <span className="text-3xl">🐉</span>
      </div>
      <p className="text-xs text-neutral-500">మీ స్టికర్ సిద్ధంగా ఉంది! 🎉</p>
    </div>
  )},
  { type: "user", lang: "bn", text: "আজকের খবর 📰" },
  { type: "bot", lang: "bn", content: (
    <div>
      <p className="text-xs text-cyan-400 mb-1">📰 শীর্ষ সংবাদ</p>
      <p className="text-xs">ভারত বনাম অস্ট্রেলিয়া ম্যাচে ভারত ৭ উইকেটে জয়ী! 🏏🇮🇳</p>
    </div>
  )},
  { type: "user", lang: "kn", text: "ವರ್ಡ್ಲ್ ಆಟ ಆಡೋಣ 🎮" },
  { type: "bot", lang: "kn", content: (
    <div>
      <div className="flex gap-1 mb-1">
        <span className="w-6 h-6 bg-green-500 rounded text-white text-xs flex items-center justify-center font-bold">ಕ</span>
        <span className="w-6 h-6 bg-yellow-500 rounded text-white text-xs flex items-center justify-center font-bold">ನ</span>
        <span className="w-6 h-6 bg-neutral-300 rounded text-white text-xs flex items-center justify-center font-bold">್ನ</span>
        <span className="w-6 h-6 bg-green-500 rounded text-white text-xs flex items-center justify-center font-bold">ಡ</span>
      </div>
      <p className="text-xs text-neutral-500">ಅದ್ಭುತ! 3/6 ಪ್ರಯತ್ನಗಳಲ್ಲಿ! 🎯</p>
    </div>
  )},
  { type: "user", lang: "gu", text: "આજનું પંચાંગ 🕉️" },
  { type: "bot", lang: "gu", content: (
    <div>
      <p className="text-xs text-amber-400 mb-1">🕉️ પંચાંગ</p>
      <p className="text-xs">તિથિ: શુક્લ એકાદશી</p>
      <p className="text-xs text-neutral-500">નક્ષત્ર: રોહિણી | યોગ: શુભ</p>
    </div>
  )},
  { type: "user", lang: "ml", text: "ബിരിയാണി റെസിപ്പി 🍚" },
  { type: "bot", lang: "ml", content: (
    <div>
      <p className="text-xs text-orange-400 mb-1">🍚 മലബാർ ബിരിയാണി</p>
      <p className="text-xs">ചേരുവകൾ: ബസ്മതി അരി, ചിക്കൻ, മസാല...</p>
      <p className="text-xs text-neutral-500 mt-1">⏱️ സമയം: 45 മിനിറ്റ്</p>
    </div>
  )},
  { type: "user", lang: "mr", text: "एक विनोद सांग 😄" },
  { type: "bot", lang: "mr", content: (
    <div>
      <p className="text-xs">शिक्षक: तुझा होमवर्क कुठे आहे?</p>
      <p className="text-xs">विद्यार्थी: कुत्र्याने खाल्ला सर! 🐕</p>
      <p className="text-xs mt-1">😂😂😂</p>
    </div>
  )},
  { type: "user", lang: "pa", text: "🎤 ਵੌਇਸ ਮੈਸੇਜ 0:05", isVoice: true },
  { type: "bot", lang: "pa", content: (
    <div>
      <p className="text-xs text-green-400 mb-1">🎤 ਵੌਇਸ ਟ੍ਰਾਂਸਕ੍ਰਿਪਟ</p>
      <p className="text-xs">&quot;ਸਤ ਸ੍ਰੀ ਅਕਾਲ ਜੀ! ਮੈਂ ਠੀਕ ਹਾਂ&quot;</p>
    </div>
  )},
  { type: "user", lang: "or", text: "ଆଜି ପାଣିପାଗ କେମିତି? ☀️" },
  { type: "bot", lang: "or", content: (
    <div>
      <p className="text-xs text-neutral-500 mb-1">🇮🇳 ଭୁବନେଶ୍ୱର</p>
      <p>🌡️ <span className="font-semibold">28°C</span> • ଆଂଶିକ ମେଘୁଆ</p>
      <p className="text-neutral-500 text-xs mt-1">💧 ଆର୍ଦ୍ରତା: 65%</p>
    </div>
  )},
  { type: "user", lang: "hi", text: "मेरी कुंडली बनाओ 🌟" },
  { type: "bot", lang: "hi", content: (
    <div>
      <p className="text-xs text-purple-400 mb-1">🌟 जन्म कुंडली</p>
      <div className="grid grid-cols-3 gap-0.5 mb-1">
        <span className="w-5 h-5 bg-violet-600/50 rounded text-[8px] flex items-center justify-center">शु</span>
        <span className="w-5 h-5 bg-neutral-200 rounded text-[8px] flex items-center justify-center">रा</span>
        <span className="w-5 h-5 bg-orange-600/50 rounded text-[8px] flex items-center justify-center">सू</span>
        <span className="w-5 h-5 bg-neutral-200 rounded text-[8px] flex items-center justify-center">के</span>
        <span className="w-5 h-5 bg-red-600/50 rounded text-[8px] flex items-center justify-center">मं</span>
        <span className="w-5 h-5 bg-neutral-200 rounded text-[8px] flex items-center justify-center">बु</span>
      </div>
      <p className="text-xs text-neutral-500">लग्न: वृषभ | चंद्र: कर्क</p>
    </div>
  )},
  { type: "user", lang: "ta", text: "PNR நிலை 2847593021 🚂" },
  { type: "bot", lang: "ta", content: (
    <div>
      <p className="text-xs text-blue-400 mb-1">🚂 ரயில் நிலை</p>
      <p className="text-xs">சென்னை → மும்பை எக்ஸ்பிரஸ்</p>
      <p className="text-xs text-green-400 mt-1">✅ உறுதி - S4/32</p>
    </div>
  )},
  { type: "user", lang: "te", text: "Hello అనువదించు 🌐" },
  { type: "bot", lang: "te", content: (
    <div>
      <p className="text-xs text-blue-400 mb-1">🌐 అనువాదం</p>
      <p className="text-xs">English: Hello</p>
      <p className="text-xs text-violet-400">తెలుగు: హలో / నమస్కారం</p>
    </div>
  )},
  { type: "user", lang: "bn", text: "এই খবরটি সত্য? 🔍" },
  { type: "bot", lang: "bn", content: (
    <div>
      <p className="text-xs text-red-400 mb-1">❌ ভুয়া খবর সতর্কতা</p>
      <p className="text-xs">এই দাবিটি মিথ্যা প্রমাণিত হয়েছে।</p>
      <p className="text-xs text-neutral-500 mt-1">📊 বিশ্বাসযোগ্যতা: 12%</p>
    </div>
  )},
  { type: "user", lang: "kn", text: "ಜನ್ಮದಿನದ ಶುಭಾಶಯ ಚಿತ್ರ 🎂" },
  { type: "bot", lang: "kn", content: (
    <div>
      <div className="w-full h-16 rounded-lg mb-1 bg-gradient-to-br from-pink-500 to-violet-600 flex items-center justify-center">
        <span className="text-2xl">🎂🎉</span>
      </div>
      <p className="text-xs text-neutral-500">ಹುಟ್ಟುಹಬ್ಬದ ಶುಭಾಶಯಗಳು! 🥳</p>
    </div>
  )},
  { type: "user", lang: "gu", text: "ક્રિકેટ સ્કોર 🏏" },
  { type: "bot", lang: "gu", content: (
    <div>
      <p className="text-xs text-green-400 mb-1">🏏 લાઈવ સ્કોર</p>
      <p className="text-xs font-semibold">IND 🇮🇳 284/3 (45 ov)</p>
      <p className="text-xs text-neutral-500">vs AUS 🇦🇺 | કોહલી 89*</p>
    </div>
  )},
  { type: "user", lang: "ml", text: "പുതിയ സിനിമ 🎬" },
  { type: "bot", lang: "ml", content: (
    <div>
      <p className="text-xs text-yellow-400 mb-1">🎬 ഈ ആഴ്ച റിലീസ്</p>
      <p className="text-xs">മഞ്ജുമ്മൽ ബോയ്സ് ⭐ 9.2</p>
      <p className="text-xs text-neutral-500 mt-1">തിയേറ്ററുകളിൽ ഇപ്പോൾ!</p>
    </div>
  )},
  { type: "user", lang: "mr", text: "प्रेरणादायी विचार 💭" },
  { type: "bot", lang: "mr", content: (
    <div>
      <p className="text-xs text-amber-400 mb-1">💭 आजचा विचार</p>
      <p className="text-xs italic">&quot;यश म्हणजे पडणे आणि पुन्हा उठणे&quot;</p>
      <p className="text-xs text-neutral-500 mt-1">- स्वामी विवेकानंद</p>
    </div>
  )},
  { type: "user", lang: "hi", text: "याद दिलाओ सुबह 8 बजे 🔔" },
  { type: "bot", lang: "hi", content: (
    <div>
      <p className="text-xs text-green-400 mb-1">✅ रिमाइंडर सेट</p>
      <p className="text-xs">⏰ सुबह 8:00 बजे</p>
      <p className="text-xs text-neutral-500 mt-1">मैं आपको याद दिलाऊंगा!</p>
    </div>
  )},
  { type: "user", lang: "en", text: "Shinchanify my photo 😜" },
  { type: "bot", lang: "en", content: (
    <div>
      <div className="w-16 h-16 rounded-xl mb-1 bg-gradient-to-br from-yellow-400 to-amber-500 flex items-center justify-center">
        <span className="text-3xl">😜</span>
      </div>
      <p className="text-xs text-neutral-500">Your Shinchan avatar is ready! 🖼️</p>
    </div>
  )},
]

// ============== PHONE MOCKUP COMPONENT (light theme) ==============
function PhoneMockup() {
  const scrollRef = useRef<HTMLDivElement>(null)
  const [isHovered, setIsHovered] = useState(false)

  useEffect(() => {
    const container = scrollRef.current
    if (!container) return

    let animationId: number
    let scrollPosition = 0
    const scrollSpeed = 0.5

    const autoScroll = () => {
      if (!isHovered && container) {
        scrollPosition += scrollSpeed
        if (scrollPosition >= container.scrollHeight - container.clientHeight) {
          scrollPosition = 0
        }
        container.scrollTop = scrollPosition
      }
      animationId = requestAnimationFrame(autoScroll)
    }

    animationId = requestAnimationFrame(autoScroll)
    return () => cancelAnimationFrame(animationId)
  }, [isHovered])

  return (
    <motion.div initial={{ opacity: 0, x: 50, rotateY: -15 }} animate={{ opacity: 1, x: 0, rotateY: 0 }} transition={{ delay: 0.5, duration: 0.8 }} className="relative flex justify-center">
      <div className="relative">
        <div className="absolute inset-0 bg-gradient-to-r from-violet-300/50 via-indigo-300/40 to-blue-300/30 rounded-[3rem] blur-3xl scale-115 animate-soft-pulse" />
        <TiltCard>
          <div className="relative w-[280px] sm:w-[320px] h-[560px] sm:h-[640px] bg-gradient-to-b from-neutral-100 to-neutral-200 rounded-[2.5rem] p-2 border border-neutral-300 shadow-[0_4px_8px_rgba(0,0,0,0.06),0_16px_40px_rgba(0,0,0,0.1),0_24px_64px_rgba(124,58,237,0.12)]">
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-32 h-7 bg-neutral-900 rounded-b-2xl z-20" />
            <div className="w-full h-full bg-gradient-to-b from-neutral-50 to-white rounded-[2rem] overflow-hidden flex flex-col">
              <div className="bg-gradient-to-r from-violet-600 to-indigo-600 px-4 py-4 pt-10 flex items-center gap-3 flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center"><Sparkles className="w-5 h-5 text-white" /></div>
                <div>
                  <p className="text-white font-semibold">D23 AI</p>
                  <p className="text-white/70 text-xs flex items-center gap-1"><span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />Online • 11+ Languages</p>
                </div>
              </div>

              <div
                ref={scrollRef}
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
                className="flex-1 overflow-y-auto p-3 space-y-3 bg-neutral-50/50 scrollbar-thin scrollbar-thumb-violet-500/30 scrollbar-track-transparent"
                style={{ scrollBehavior: isHovered ? 'smooth' : 'auto' }}
              >
                {phoneChatMessages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: msg.type === 'user' ? 20 : -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + i * 0.1 }}
                    className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.type === 'user' ? (
                      <div className={`max-w-[80%] bg-violet-600 text-white text-sm px-3 py-2 rounded-2xl rounded-br-md ${(msg as any).isVoice ? 'flex items-center gap-2' : ''}`}>
                        {(msg as any).isVoice && <Mic className="w-4 h-4" />}
                        {msg.text}
                      </div>
                    ) : (
                      <div className="max-w-[85%] bg-white text-neutral-800 text-sm px-3 py-2 rounded-2xl rounded-bl-md border border-neutral-200 shadow-sm">
                        {(msg as any).content}
                      </div>
                    )}
                  </motion.div>
                ))}

                {phoneChatMessages.map((msg, i) => (
                  <div
                    key={`dup-${i}`}
                    className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.type === 'user' ? (
                      <div className={`max-w-[80%] bg-violet-600 text-white text-sm px-3 py-2 rounded-2xl rounded-br-md ${(msg as any).isVoice ? 'flex items-center gap-2' : ''}`}>
                        {(msg as any).isVoice && <Mic className="w-4 h-4" />}
                        {msg.text}
                      </div>
                    ) : (
                      <div className="max-w-[85%] bg-white text-neutral-800 text-sm px-3 py-2 rounded-2xl rounded-bl-md border border-neutral-200 shadow-sm">
                        {(msg as any).content}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="absolute top-[76px] left-2 right-2 h-6 bg-gradient-to-b from-neutral-50 to-transparent pointer-events-none z-10 rounded-t-2xl" />
              <div className="absolute bottom-[60px] left-2 right-2 h-6 bg-gradient-to-t from-white to-transparent pointer-events-none z-10" />

              <div className="flex-shrink-0 p-3 bg-white">
                <div className="flex items-center gap-2 bg-neutral-100 rounded-full px-4 py-2.5 border border-neutral-200">
                  <span className="text-neutral-400 text-sm">Type a message...</span>
                  <div className="ml-auto flex items-center gap-2"><Mic className="w-5 h-5 text-neutral-400" /></div>
                </div>
              </div>
            </div>
          </div>
        </TiltCard>
      </div>
    </motion.div>
  )
}

// ============== HEADER ==============
function Header() {
  const [scrolled, setScrolled] = useState(false)
  const t = useTranslations()

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50)
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  return (
    <header className={cn("fixed top-0 left-0 right-0 z-50 transition-all duration-500", scrolled ? "bg-white/80 backdrop-blur-xl border-b border-neutral-200 shadow-sm" : "")}>
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" scroll={true} className="flex items-center gap-2 cursor-pointer z-10">
            <Image src="/d23ai-logo-v8.svg" alt="D23" width={40} height={40} className="cursor-pointer hover:scale-110 transition-transform" priority />
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            <Link href="#features" className="relative text-sm text-neutral-500 hover:text-neutral-900 transition-colors group">
              {t.nav.features}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-violet-500 to-indigo-500 group-hover:w-full transition-all duration-300" />
            </Link>
            <Link href="/about" className="relative text-sm text-neutral-500 hover:text-neutral-900 transition-colors group">
              {t.nav.about}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-violet-500 to-indigo-500 group-hover:w-full transition-all duration-300" />
            </Link>
            <Link href="#contact" className="relative text-sm text-neutral-500 hover:text-neutral-900 transition-colors group">
              {t.nav.contact}
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-violet-500 to-indigo-500 group-hover:w-full transition-all duration-300" />
            </Link>
          </nav>

          <div className="flex items-center gap-4">
            <LanguageSwitcher variant="pill" />
            <MagneticButton>
              <Link href="https://wa.me/919934438606?text=Hey%20D23%20AI%21%20What%20can%20you%20do%3F" target="_blank" className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-sm font-medium shadow-lg shadow-violet-500/15 hover:shadow-violet-500/30 transition-shadow">
                <Zap className="h-4 w-4" />
                {t.nav.getStarted}
              </Link>
            </MagneticButton>
          </div>
        </div>
      </div>
    </header>
  )
}

// ============== HERO SECTION ==============
function HeroSection() {
  const ref = useRef(null)
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] })
  const y = useTransform(scrollYProgress, [0, 1], [0, 200])
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0])
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.95])
  const t = useTranslations()
  const content = useLandingContent()

  const parseStatValue = (val: string) => {
    const match = val.match(/^([<>])?(\d+)(.*)$/);
    if (match) {
      return { prefix: match[1] || "", value: parseInt(match[2]), suffix: match[3] || "" };
    }
    return { prefix: "", value: 0, suffix: val };
  };

  const stats = content.stats.map((stat) => {
    const parsed = parseStatValue(stat.value);
    return {
      value: parsed.value,
      prefix: parsed.prefix,
      suffix: parsed.suffix,
      label: stat.label,
      icon: stat.icon,
    };
  });

  return (
    <section ref={ref} className="relative min-h-screen flex items-center justify-center overflow-hidden">
      <div className="absolute inset-0 bg-white">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_80%_at_50%_-20%,rgba(139,92,246,0.15),rgba(255,255,255,0))]" />
        </div>
        <div className="absolute top-20 left-[10%] w-[500px] h-[500px] bg-gradient-to-r from-violet-200/40 to-indigo-200/30 rounded-full blur-[100px] animate-[float1_20s_ease-in-out_infinite]" />
        <div className="absolute bottom-20 right-[10%] w-[400px] h-[400px] bg-gradient-to-r from-blue-200/30 to-indigo-200/20 rounded-full blur-[100px] animate-[float2_15s_ease-in-out_infinite]" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(139,92,246,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(139,92,246,0.05)_1px,transparent_1px)] bg-[size:60px_60px]" />
      </div>

      <motion.div style={{ y, opacity, scale }} className="relative z-10 w-full max-w-7xl mx-auto px-6 pt-28 pb-12">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-4 items-center">
          <div className="text-center lg:text-left">
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-violet-300/60 bg-gradient-to-r from-violet-100/80 to-indigo-100/80 backdrop-blur-sm mb-6 shadow-sm">
              <motion.div animate={{ scale: [1, 1.3, 1] }} transition={{ duration: 2, repeat: Infinity }} className="relative">
                <span className="flex h-2 w-2 rounded-full bg-green-500" />
                <span className="absolute inset-0 h-2 w-2 rounded-full bg-green-500 animate-ping" />
              </motion.div>
              <span className="text-sm font-medium text-violet-700">{t.hero.badge}</span>
            </motion.div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-neutral-900 mb-6 leading-[1.1] tracking-tight">
              <span className="whitespace-nowrap"><TextReveal>{content.hero.title}</TextReveal></span>
              <br />
              <span className="relative">
                <span className="text-neutral-400">{content.hero.subtitle} </span>
                <span className="relative">
                  <RotatingWord words={content.hero.rotatingWords} />
                  <motion.span className="absolute -bottom-2 left-0 right-0 h-1 bg-gradient-to-r from-violet-500 to-indigo-500 rounded-full" initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ delay: 1, duration: 0.8 }} />
                </span>
              </span>
            </h1>

            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.6 }} className="text-lg md:text-xl text-neutral-500 max-w-xl mx-auto lg:mx-0 mb-8">{content.hero.description}</motion.p>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.8 }} className="flex flex-wrap items-center justify-center lg:justify-start gap-4 mb-8">
              <MagneticButton>
                <Link href={`${content.hero.whatsappLink}?text=Hey%20D23%20AI%21%20What%20can%20you%20do%3F`} target="_blank" className="group relative flex items-center gap-3 px-8 py-4 rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-semibold overflow-hidden shadow-[0_2px_4px_rgba(124,58,237,0.15),0_8px_24px_rgba(124,58,237,0.3)] hover:shadow-[0_4px_8px_rgba(124,58,237,0.2),0_12px_32px_rgba(124,58,237,0.4)] transition-shadow">
                  <span className="absolute inset-0 bg-gradient-to-r from-violet-500 to-indigo-500 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                  <span className="absolute inset-0 shadow-[inset_0_1px_1px_rgba(255,255,255,0.3)]" />
                  <MessageCircle className="h-5 w-5 relative z-10" />
                  <span className="relative z-10">{content.hero.ctaPrimary}</span>
                  <ArrowRight className="h-5 w-5 relative z-10 group-hover:translate-x-1 transition-transform" />
                </Link>
              </MagneticButton>
              <MagneticButton>
                <Link href="/chat" className="group flex items-center gap-3 px-8 py-4 rounded-2xl border-2 border-neutral-200 bg-white text-neutral-900 font-semibold shadow-sm hover:shadow-md hover:border-neutral-300 hover:-translate-y-0.5 transition-all">
                  <Play className="h-4 w-4 group-hover:scale-110 transition-transform" />
                  {content.hero.ctaSecondary}
                </Link>
              </MagneticButton>
            </motion.div>

            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1 }} className="flex flex-wrap items-center justify-center lg:justify-start gap-3">
              <div className="relative group cursor-pointer">
                <div className="flex items-center gap-3 px-5 py-2.5 rounded-xl bg-white border border-neutral-200 shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.06)] hover:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_8px_20px_rgba(0,0,0,0.08)] hover:border-neutral-300 transition-all">
                  <svg className="w-7 h-7 text-neutral-900" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.81-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>
                  <div className="text-left">
                    <p className="text-[9px] text-neutral-400 uppercase tracking-wider">{t.hero.comingSoon}</p>
                    <p className="text-neutral-900 font-medium text-sm">{t.hero.appStore}</p>
                  </div>
                </div>
                <span className="absolute -top-1.5 -right-1.5 px-2 py-0.5 rounded-full bg-gradient-to-r from-violet-500 to-indigo-500 text-[9px] text-white font-bold shadow-lg">{t.hero.soon}</span>
              </div>
              <div className="relative group cursor-pointer">
                <div className="flex items-center gap-3 px-5 py-2.5 rounded-xl bg-white border border-neutral-200 shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.06)] hover:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_8px_20px_rgba(0,0,0,0.08)] hover:border-neutral-300 transition-all">
                  <svg className="w-7 h-7 text-neutral-900" viewBox="0 0 24 24" fill="currentColor"><path d="M3.609 1.814L13.792 12 3.61 22.186a.996.996 0 0 1-.61-.92V2.734a1 1 0 0 1 .609-.92zm10.89 10.893l2.302 2.302-10.937 6.333 8.635-8.635zm3.199-3.198l2.807 1.626a1 1 0 0 1 0 1.73l-2.808 1.626L15.206 12l2.492-2.491zM5.864 2.658L16.8 8.99l-2.302 2.302-8.634-8.634z"/></svg>
                  <div className="text-left">
                    <p className="text-[9px] text-neutral-400 uppercase tracking-wider">{t.hero.comingSoon}</p>
                    <p className="text-neutral-900 font-medium text-sm">{t.hero.playStore}</p>
                  </div>
                </div>
                <span className="absolute -top-1.5 -right-1.5 px-2 py-0.5 rounded-full bg-gradient-to-r from-violet-500 to-indigo-500 text-[9px] text-white font-bold shadow-lg">{t.hero.soon}</span>
              </div>
            </motion.div>
          </div>

          <PhoneMockup />
        </div>

        <motion.div initial={{ opacity: 0, y: 40 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.2 }} className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-16">
          {stats.map((stat, i) => (
            <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 1.3 + i * 0.1 }} whileHover={{ scale: 1.02, y: -2 }} className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-violet-500/10 to-indigo-500/10 rounded-2xl blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
              <div className="relative p-6 rounded-2xl bg-white border border-neutral-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04),0_6px_16px_rgba(0,0,0,0.06)] hover:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_12px_32px_rgba(0,0,0,0.08)] hover:border-neutral-300/80 transition-all overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-violet-500 to-indigo-500" />
                <span className="text-2xl mb-2 block">{stat.icon}</span>
                <div className="text-3xl md:text-4xl font-bold text-neutral-900 mb-1">{stat.prefix || ""}<AnimatedCounter value={stat.value} suffix={stat.suffix} /></div>
                <div className="text-sm text-neutral-400">{stat.label}</div>
              </div>
            </motion.div>
          ))}
        </motion.div>
      </motion.div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 1.5 }} className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <motion.div animate={{ y: [0, 8, 0] }} transition={{ duration: 1.5, repeat: Infinity }} className="flex flex-col items-center gap-2">
          <span className="text-xs text-neutral-400 uppercase tracking-widest">Scroll</span>
          <ChevronDown className="h-5 w-5 text-neutral-400" />
        </motion.div>
      </motion.div>
    </section>
  )
}

// ============== HOW IT WORKS SECTION (NEW) ==============
function HowItWorksSection() {
  const t = useTranslations()
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  const steps = [
    { icon: <Phone className="h-7 w-7 text-white" />, color: "from-violet-500 to-purple-500", titleKey: "step1Title", descKey: "step1Desc", number: "1" },
    { icon: <MessageCircle className="h-7 w-7 text-white" />, color: "from-indigo-500 to-blue-500", titleKey: "step2Title", descKey: "step2Desc", number: "2" },
    { icon: <Sparkles className="h-7 w-7 text-white" />, color: "from-blue-500 to-cyan-500", titleKey: "step3Title", descKey: "step3Desc", number: "3" },
  ]

  return (
    <section ref={ref} className="py-24 px-6 bg-gradient-to-b from-violet-50/30 via-white to-white">
      <div className="max-w-5xl mx-auto">
        <StaggerContainer className="text-center mb-20">
          <StaggerItem>
            <span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">{t.howItWorks?.label ?? "How It Works"}</span>
          </StaggerItem>
          <StaggerItem>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mt-4">
              {t.howItWorks?.title ?? "Get started in"} <GradientText>{t.howItWorks?.titleHighlight ?? "3 simple steps"}</GradientText>
            </h2>
          </StaggerItem>
        </StaggerContainer>

        <div className="grid grid-cols-3 gap-4 md:gap-8 relative">
          <div className="hidden md:block absolute top-10 md:top-[4.5rem] left-[20%] right-[20%] h-[2px] bg-gradient-to-r from-violet-300 via-indigo-300 to-blue-300" />

          {steps.map((step, i) => (
            <motion.div
              key={step.number}
              initial={{ opacity: 0, y: 30 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: i * 0.2 }}
              className="relative text-center"
            >
              <div className="bg-white rounded-2xl p-4 md:p-6 shadow-[0_1px_3px_rgba(0,0,0,0.04),0_6px_16px_rgba(0,0,0,0.06)] border border-neutral-200/80">
                <div className="relative z-10 inline-block mb-4 md:mb-6">
                  <div className="absolute inset-0 bg-gradient-to-br from-violet-400/20 to-indigo-400/20 rounded-2xl blur-xl scale-150" />
                  <div className={cn("relative w-14 h-14 md:w-16 md:h-16 lg:w-20 lg:h-20 rounded-xl md:rounded-2xl bg-gradient-to-br flex items-center justify-center shadow-lg", step.color)}>
                    <span className="[&>svg]:w-5 [&>svg]:h-5 md:[&>svg]:w-7 md:[&>svg]:h-7 lg:[&>svg]:w-8 lg:[&>svg]:h-8">{step.icon}</span>
                  </div>
                  <span className="absolute -top-1.5 -right-1.5 md:-top-2 md:-right-2 w-5 h-5 md:w-7 md:h-7 rounded-full bg-white border-2 border-violet-500 text-violet-600 text-[10px] md:text-xs font-bold flex items-center justify-center shadow-sm">{step.number}</span>
                </div>
                <h3 className="text-sm md:text-xl font-semibold text-neutral-900 mb-1 md:mb-2">{(t.howItWorks as any)?.[step.titleKey] ?? step.titleKey}</h3>
                <p className="text-xs md:text-base text-neutral-500 hidden sm:block">{(t.howItWorks as any)?.[step.descKey] ?? step.descKey}</p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}

// ============== ANIMATED DEMO SHOWCASE ==============
const demoConversations = [
  {
    id: "weather",
    icon: "🌤️",
    title: "Weather",
    color: "from-sky-500 to-blue-600",
    conversation: [
      { type: "user", text: "आज दिल्ली का मौसम कैसा है?", lang: "हिंदी" },
      { type: "bot", text: "दिल्ली में आज:\n🌡️ 28°C\n☀️ साफ आसमान\n💨 हवा: 12 km/h\n💧 नमी: 45%", lang: "हिंदी" },
    ],
  },
  {
    id: "image",
    icon: "🎨",
    title: "AI Images",
    color: "from-orange-500 to-pink-600",
    conversation: [
      { type: "user", text: "Generate a sunset over mountains", lang: "English" },
      { type: "bot", text: "Creating your image...", lang: "English", isImage: true },
    ],
  },
  {
    id: "translate",
    icon: "🌐",
    title: "Translate",
    color: "from-emerald-500 to-teal-600",
    conversation: [
      { type: "user", text: "How do you say 'thank you' in Tamil?", lang: "English" },
      { type: "bot", text: "நன்றி (Nandri)\n\nUsage: நன்றி சொல்கிறேன் 🙏", lang: "தமிழ்" },
    ],
  },
  {
    id: "factcheck",
    icon: "🔍",
    title: "Fact Check",
    color: "from-red-500 to-rose-600",
    conversation: [
      { type: "user", text: "Is this news real? [forwarded message]", lang: "English" },
      { type: "bot", text: "⚠️ MISLEADING\n\nThis claim is partially false. Here's what we found...", lang: "English" },
    ],
  },
  {
    id: "games",
    icon: "🎮",
    title: "Games",
    color: "from-violet-500 to-purple-600",
    conversation: [
      { type: "user", text: "ಪದ ಆಟ ಆಡೋಣ!", lang: "ಕನ್ನಡ" },
      { type: "bot", text: "🟩🟨🟩🟩🟩\n\nಅದ್ಭುತ! 3/6 ಪ್ರಯತ್ನಗಳಲ್ಲಿ ಗೆದ್ದಿರಿ! 🎉", lang: "ಕನ್ನಡ", isGame: true },
    ],
  },
  {
    id: "stickers",
    icon: "🎭",
    title: "Stickers",
    color: "from-amber-500 to-yellow-600",
    conversation: [
      { type: "user", text: "Make me a sticker of a happy dog", lang: "English" },
      { type: "bot", text: "Here's your custom sticker! 🐕", lang: "English", isSticker: true },
    ],
  },
]

const languageFlags = [
  { lang: "हिंदी", flag: "🇮🇳" },
  { lang: "தமிழ்", flag: "🇮🇳" },
  { lang: "తెలుగు", flag: "🇮🇳" },
  { lang: "ಕನ್ನಡ", flag: "🇮🇳" },
  { lang: "മലയാളം", flag: "🇮🇳" },
  { lang: "বাংলা", flag: "🇮🇳" },
  { lang: "मराठी", flag: "🇮🇳" },
  { lang: "ગુજરાતી", flag: "🇮🇳" },
  { lang: "ਪੰਜਾਬੀ", flag: "🇮🇳" },
  { lang: "ଓଡ଼ିଆ", flag: "🇮🇳" },
  { lang: "English", flag: "🌐" },
]

function AnimatedDemoShowcase() {
  const [activeDemo, setActiveDemo] = useState(0)
  const [isTyping, setIsTyping] = useState(false)
  const [showResponse, setShowResponse] = useState(false)
  const ref = useRef(null)
  const isInView = useInView(ref, { once: true, margin: "-100px" })

  useEffect(() => {
    if (!isInView) return
    const interval = setInterval(() => {
      setShowResponse(false)
      setIsTyping(false)
      setTimeout(() => {
        setActiveDemo((prev) => (prev + 1) % demoConversations.length)
      }, 300)
    }, 5000)
    return () => clearInterval(interval)
  }, [isInView])

  useEffect(() => {
    if (!isInView) return
    setIsTyping(true)
    const timer = setTimeout(() => {
      setIsTyping(false)
      setShowResponse(true)
    }, 1200)
    return () => clearTimeout(timer)
  }, [activeDemo, isInView])

  const currentDemo = demoConversations[activeDemo]

  return (
    <section ref={ref} className="py-24 px-6 overflow-hidden relative">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-[10%] w-[400px] h-[400px] bg-gradient-to-r from-violet-100/40 to-indigo-100/30 rounded-full blur-[100px]" />
        <div className="absolute bottom-20 right-[15%] w-[350px] h-[350px] bg-gradient-to-r from-blue-100/30 to-violet-100/20 rounded-full blur-[100px]" />
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ duration: 60, repeat: Infinity, ease: "linear" }}
          className="absolute -top-1/2 -right-1/2 w-full h-full bg-gradient-conic from-violet-100/30 via-transparent to-indigo-100/30 blur-3xl"
        />
      </div>

      <div className="max-w-6xl mx-auto relative z-10">
        <StaggerContainer className="text-center mb-16">
          <StaggerItem>
            <motion.div
              initial={{ scale: 0 }}
              animate={isInView ? { scale: 1 } : {}}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-50 border border-violet-200 mb-4"
            >
              <motion.div
                animate={{ rotate: [0, 360] }}
                transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
              >
                <Sparkles className="w-4 h-4 text-violet-600" />
              </motion.div>
              <span className="text-violet-600 text-sm font-medium">Interactive Demo</span>
            </motion.div>
          </StaggerItem>
          <StaggerItem>
            <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mt-4">
              Try D23 AI <GradientText>Features</GradientText>
            </h2>
          </StaggerItem>
          <StaggerItem>
            <p className="text-neutral-500 mt-4 max-w-xl mx-auto text-lg">
              Click on any feature to see how D23 AI responds in real-time
            </p>
          </StaggerItem>
        </StaggerContainer>

        <div className="grid lg:grid-cols-5 gap-8 items-start">
          <div className="lg:col-span-2 space-y-3">
            {demoConversations.map((demo, i) => (
              <motion.button
                key={demo.id}
                onClick={() => {
                  setShowResponse(false)
                  setIsTyping(false)
                  setActiveDemo(i)
                }}
                initial={{ opacity: 0, x: -30 }}
                animate={isInView ? { opacity: 1, x: 0 } : {}}
                transition={{ delay: i * 0.1 }}
                whileHover={{ x: 8 }}
                className={cn(
                  "w-full flex items-center gap-4 p-4 rounded-2xl border transition-all duration-300 text-left group",
                  i === activeDemo
                    ? "bg-gradient-to-r from-violet-50 to-indigo-50 border-violet-300 ring-1 ring-violet-200 shadow-[0_2px_4px_rgba(0,0,0,0.04),0_8px_24px_rgba(124,58,237,0.12)]"
                    : "bg-white border-neutral-200 shadow-[0_1px_3px_rgba(0,0,0,0.04)] hover:border-neutral-300 hover:shadow-[0_1px_3px_rgba(0,0,0,0.04),0_4px_12px_rgba(0,0,0,0.06)]"
                )}
              >
                <div className={cn(
                  "w-14 h-14 rounded-xl flex items-center justify-center text-2xl transition-transform duration-300",
                  i === activeDemo ? `bg-gradient-to-br ${demo.color} shadow-lg` : "bg-neutral-100",
                  "group-hover:scale-110"
                )}>
                  {demo.icon}
                </div>
                <div className="flex-1">
                  <h3 className={cn(
                    "font-semibold transition-colors",
                    i === activeDemo ? "text-neutral-900" : "text-neutral-600"
                  )}>
                    {demo.title}
                  </h3>
                  <p className="text-xs text-neutral-400 mt-0.5">
                    {demo.conversation[0].text.slice(0, 30)}...
                  </p>
                </div>
                {i === activeDemo && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="w-1.5 h-10 rounded-full bg-gradient-to-b from-violet-500 to-indigo-500"
                  />
                )}
              </motion.button>
            ))}
          </div>

          {/* Chat Preview - stays dark themed */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.3 }}
            className="lg:col-span-3"
          >
            <div className="relative">
              <motion.div
                key={activeDemo}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className={cn(
                  "absolute -inset-4 rounded-3xl blur-3xl opacity-20",
                  `bg-gradient-to-r ${currentDemo.color}`
                )}
              />

              <div className="relative bg-zinc-900/90 rounded-3xl border border-neutral-300/60 overflow-hidden backdrop-blur-xl shadow-[0_4px_8px_rgba(0,0,0,0.06),0_16px_40px_rgba(0,0,0,0.12)]">
                <div className={cn("p-4 flex items-center gap-3 bg-gradient-to-r", currentDemo.color)}>
                  <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center backdrop-blur-sm">
                    <span className="text-2xl">{currentDemo.icon}</span>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-white font-bold text-lg">{currentDemo.title}</h3>
                    <div className="flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                      <span className="text-white/70 text-sm">D23 AI is ready</span>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <div className="w-3 h-3 rounded-full bg-white/20" />
                    <div className="w-3 h-3 rounded-full bg-white/20" />
                    <div className="w-3 h-3 rounded-full bg-white/20" />
                  </div>
                </div>

                <div className="p-6 min-h-[320px] space-y-4">
                  <motion.div
                    key={`user-${activeDemo}`}
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex justify-end"
                  >
                    <div className="max-w-[80%]">
                      <div className="bg-violet-600 text-white px-4 py-3 rounded-2xl rounded-br-md shadow-lg">
                        <p className="text-sm">{currentDemo.conversation[0].text}</p>
                      </div>
                      <p className="text-xs text-zinc-500 mt-1 text-right">{currentDemo.conversation[0].lang}</p>
                    </div>
                  </motion.div>

                  <AnimatePresence mode="wait">
                    {isTyping && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        className="flex justify-start"
                      >
                        <div className="bg-zinc-800 px-4 py-3 rounded-2xl rounded-bl-md border border-zinc-700">
                          <div className="flex gap-1.5">
                            <motion.span animate={{ y: [0, -5, 0] }} transition={{ duration: 0.5, repeat: Infinity, delay: 0 }} className="w-2 h-2 bg-zinc-500 rounded-full" />
                            <motion.span animate={{ y: [0, -5, 0] }} transition={{ duration: 0.5, repeat: Infinity, delay: 0.1 }} className="w-2 h-2 bg-zinc-500 rounded-full" />
                            <motion.span animate={{ y: [0, -5, 0] }} transition={{ duration: 0.5, repeat: Infinity, delay: 0.2 }} className="w-2 h-2 bg-zinc-500 rounded-full" />
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {showResponse && (
                      <motion.div
                        key={`bot-${activeDemo}`}
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        className="flex justify-start"
                      >
                        <div className="max-w-[85%]">
                          <div className="bg-zinc-800 text-white px-4 py-3 rounded-2xl rounded-bl-md border border-zinc-700/50 shadow-lg">
                            {(currentDemo.conversation[1] as any).isImage && (
                              <div className="w-full h-40 rounded-xl mb-3 overflow-hidden bg-gradient-to-br from-orange-400 to-pink-600 flex items-center justify-center">
                                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.3, type: "spring" }}>
                                  <ImageIcon className="w-12 h-12 text-white/80" />
                                </motion.div>
                              </div>
                            )}
                            {(currentDemo.conversation[1] as any).isGame && (
                              <div className="flex gap-1 mb-2">
                                {['🟩', '🟨', '🟩', '🟩', '🟩'].map((box, i) => (
                                  <motion.span key={i} initial={{ scale: 0, rotate: -180 }} animate={{ scale: 1, rotate: 0 }} transition={{ delay: 0.1 * i, type: "spring" }} className="w-8 h-8 flex items-center justify-center text-lg">
                                    {box}
                                  </motion.span>
                                ))}
                              </div>
                            )}
                            {(currentDemo.conversation[1] as any).isSticker && (
                              <motion.div initial={{ scale: 0, rotate: -20 }} animate={{ scale: 1, rotate: 0 }} transition={{ type: "spring" }} className="w-24 h-24 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-2xl mb-2 flex items-center justify-center text-5xl">
                                🐕
                              </motion.div>
                            )}
                            <p className="text-sm whitespace-pre-line">{currentDemo.conversation[1].text}</p>
                          </div>
                          <p className="text-xs text-zinc-500 mt-1">{currentDemo.conversation[1].lang}</p>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>

                <div className="p-4 border-t border-zinc-800 bg-black/30">
                  <div className="flex items-center gap-3 bg-zinc-800/50 rounded-full px-4 py-3 border border-zinc-700/50">
                    <input type="text" placeholder="Type a message in any language..." className="flex-1 bg-transparent text-white placeholder-zinc-500 text-sm outline-none" disabled />
                    <div className="flex gap-2">
                      <div className="w-8 h-8 rounded-full bg-zinc-700/50 flex items-center justify-center">
                        <Mic className="w-4 h-4 text-neutral-500" />
                      </div>
                      <div className="w-8 h-8 rounded-full bg-gradient-to-r from-violet-500 to-indigo-500 flex items-center justify-center">
                        <ArrowRight className="w-4 h-4 text-white" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.5 }}
              className="mt-6 p-4 rounded-2xl bg-neutral-50 border border-neutral-200"
            >
              <p className="text-xs text-neutral-400 mb-3 uppercase tracking-wider text-center">Works in 11+ Languages Worldwide</p>
              <div className="flex flex-wrap justify-center gap-2">
                {languageFlags.map((item, i) => (
                  <motion.span
                    key={item.lang}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={isInView ? { opacity: 1, scale: 1 } : {}}
                    transition={{ delay: 0.6 + i * 0.05 }}
                    whileHover={{ scale: 1.1, y: -2 }}
                    className="px-3 py-1.5 rounded-full bg-white border border-neutral-200 text-xs text-neutral-700 cursor-default flex items-center gap-1.5 shadow-sm"
                  >
                    <span>{item.flag}</span>
                    <span>{item.lang}</span>
                  </motion.span>
                ))}
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  )
}

// ============== FEATURES SECTION ==============
function FeaturesSection() {
  const t = useTranslations()
  const features = [
    { id: "languages", icon: <Languages className="h-6 w-6" />, titleKey: "languages", color: "from-violet-500 to-purple-500" },
    { id: "voice", icon: <Mic className="h-6 w-6" />, titleKey: "voice", color: "from-indigo-500 to-violet-500" },
    { id: "images", icon: <ImageIcon className="h-6 w-6" />, titleKey: "images", color: "from-orange-500 to-red-500" },
    { id: "factCheck", icon: <ShieldCheck className="h-6 w-6" />, titleKey: "factCheck", color: "from-cyan-500 to-blue-500" },
    { id: "stickers", icon: <Sticker className="h-6 w-6" />, titleKey: "stickers", color: "from-green-500 to-emerald-500" },
    { id: "games", icon: <Gamepad2 className="h-6 w-6" />, titleKey: "games", color: "from-amber-500 to-yellow-500" },
  ]

  return (
    <section id="features" className="py-24 px-6">
      <SectionDivider />
      <div className="max-w-6xl mx-auto pt-8">
        <StaggerContainer className="text-center mb-20">
          <StaggerItem><span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">{t.features.label}</span></StaggerItem>
          <StaggerItem><h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mt-4">{t.features.title1}<br /><GradientText>{t.features.title2}</GradientText></h2></StaggerItem>
        </StaggerContainer>
        <StaggerContainer className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature) => {
            const featureData = t.features[feature.titleKey as keyof typeof t.features] as { title: string; desc: string }
            return (
              <StaggerItem key={feature.id}>
                <TiltCard className="h-full">
                  <PremiumCard className="h-full">
                    <div className="p-6 h-full">
                      <div className="relative inline-block mb-5">
                        <div className={cn("absolute inset-0 rounded-2xl blur-xl opacity-30 scale-150 bg-gradient-to-br", feature.color)} />
                        <motion.div whileHover={{ scale: 1.1, rotate: 5 }} className={cn("relative w-14 h-14 rounded-2xl flex items-center justify-center bg-gradient-to-br text-white", feature.color)}>{feature.icon}</motion.div>
                      </div>
                      <h3 className="text-xl font-semibold text-neutral-900 mb-2">{featureData?.title}</h3>
                      <p className="text-neutral-500">{featureData?.desc}</p>
                    </div>
                  </PremiumCard>
                </TiltCard>
              </StaggerItem>
            )
          })}
        </StaggerContainer>
      </div>
    </section>
  )
}

// ============== TESTIMONIALS SECTION (NEW) ==============
function TestimonialsSection() {
  const t = useTranslations()

  const testimonials = [
    { quoteKey: "t1Quote", nameKey: "t1Name", cityKey: "t1City", stars: 5 },
    { quoteKey: "t2Quote", nameKey: "t2Name", cityKey: "t2City", stars: 5 },
    { quoteKey: "t3Quote", nameKey: "t3Name", cityKey: "t3City", stars: 5 },
    { quoteKey: "t4Quote", nameKey: "t4Name", cityKey: "t4City", stars: 4 },
    { quoteKey: "t5Quote", nameKey: "t5Name", cityKey: "t5City", stars: 5 },
    { quoteKey: "t6Quote", nameKey: "t6Name", cityKey: "t6City", stars: 5 },
  ]

  return (
    <section className="py-24 px-6 bg-gradient-to-b from-indigo-50/25 via-violet-50/20 to-white">
      <div className="max-w-6xl mx-auto">
        <StaggerContainer className="text-center mb-20">
          <StaggerItem><span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">{t.testimonials?.label ?? "Testimonials"}</span></StaggerItem>
          <StaggerItem><h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mt-4">{t.testimonials?.title ?? "Loved by users across"} <GradientText>{t.testimonials?.titleHighlight ?? "India"}</GradientText></h2></StaggerItem>
        </StaggerContainer>
        <StaggerContainer className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((item) => (
            <StaggerItem key={item.nameKey}>
              <motion.div whileHover={{ y: -4 }} className="relative bg-white rounded-2xl p-8 border border-neutral-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04),0_6px_16px_rgba(0,0,0,0.06)] hover:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_12px_32px_rgba(0,0,0,0.08)] transition-all h-full flex flex-col">
                <span className="absolute top-4 right-6 text-7xl text-violet-100 font-serif leading-none select-none pointer-events-none">&ldquo;</span>
                <div className="inline-flex gap-0.5 mb-4 px-3 py-1 rounded-full bg-amber-50 border border-amber-200/50 w-fit">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <Star key={i} className={cn("w-4 h-4", i < item.stars ? "text-amber-400 fill-amber-400" : "text-neutral-200")} />
                  ))}
                </div>
                <p className="text-neutral-600 flex-1 mb-4 relative z-10">&quot;{(t.testimonials as any)?.[item.quoteKey] ?? ""}&quot;</p>
                <div className="flex items-center gap-3 pt-4 border-t border-neutral-100">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center text-white font-semibold text-sm ring-2 ring-white shadow-md">
                    {((t.testimonials as any)?.[item.nameKey] ?? "U")[0]}
                  </div>
                  <div>
                    <p className="font-semibold text-neutral-900 text-sm">{(t.testimonials as any)?.[item.nameKey] ?? ""}</p>
                    <p className="text-neutral-400 text-xs">{(t.testimonials as any)?.[item.cityKey] ?? ""}</p>
                  </div>
                </div>
              </motion.div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </section>
  )
}

// ============== COMPARISON SECTION (NEW) ==============
function ComparisonSection() {
  const t = useTranslations()

  const rows = [
    { key: "indianLanguages", d23: true, chatgpt: "partial", google: true },
    { key: "whatsappNative", d23: true, chatgpt: false, google: false },
    { key: "voiceAI", d23: true, chatgpt: true, google: false },
    { key: "imageGen", d23: true, chatgpt: true, google: false },
    { key: "stickers", d23: true, chatgpt: false, google: false },
    { key: "games", d23: true, chatgpt: false, google: false },
    { key: "free", d23: true, chatgpt: false, google: true },
  ]

  const renderCell = (value: boolean | string) => {
    if (value === true) return <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-green-50 border border-green-200/60"><Check className="w-4 h-4 text-green-500" /></span>
    if (value === false) return <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-red-50 border border-red-200/60"><XIcon className="w-4 h-4 text-red-400" /></span>
    return <span className="inline-flex items-center justify-center px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200/60 text-amber-600 text-xs font-medium">Partial</span>
  }

  return (
    <section className="py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <StaggerContainer className="text-center mb-20">
          <StaggerItem><span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">{t.comparison?.label ?? "Why D23 AI"}</span></StaggerItem>
          <StaggerItem><h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mt-4">{t.comparison?.title ?? "See how D23 AI"} <GradientText>{t.comparison?.titleHighlight ?? "compares"}</GradientText></h2></StaggerItem>
        </StaggerContainer>

        <motion.div initial={{ opacity: 0, y: 30 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="bg-white rounded-3xl border border-neutral-200/80 shadow-[0_2px_4px_rgba(0,0,0,0.04),0_12px_32px_rgba(0,0,0,0.08)] overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="text-left p-4 text-neutral-500 font-medium text-sm">{t.comparison?.feature ?? "Feature"}</th>
                  <th className="p-4 text-center bg-violet-100/80">
                    <span className="font-bold text-violet-600">{t.comparison?.d23 ?? "D23 AI"}</span>
                    <p className="text-[10px] text-violet-400 font-medium mt-0.5">Recommended</p>
                  </th>
                  <th className="p-4 text-center text-neutral-500 font-medium text-sm">{t.comparison?.chatgpt ?? "ChatGPT"}</th>
                  <th className="p-4 text-center text-neutral-500 font-medium text-sm">{t.comparison?.googleTranslate ?? "Google Translate"}</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row, i) => (
                  <tr key={row.key} className={cn("border-b border-neutral-100 hover:bg-violet-50/30 transition-colors", i % 2 === 0 ? "bg-neutral-50/50" : "")}>
                    <td className="p-4 text-neutral-700 text-sm font-medium">{(t.comparison as any)?.[row.key] ?? row.key}</td>
                    <td className="p-4 text-center bg-violet-50/20">{renderCell(row.d23)}</td>
                    <td className="p-4 text-center">{renderCell(row.chatgpt)}</td>
                    <td className="p-4 text-center">{renderCell(row.google)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </section>
  )
}

// ============== ABOUT SECTION ==============
function AboutSection() {
  return (
    <section id="about" className="py-24 px-6 relative overflow-hidden">
      <div className="absolute inset-0 bg-white" />
      <div className="absolute top-20 left-[5%] w-[400px] h-[400px] bg-gradient-to-r from-violet-100/30 to-indigo-100/20 rounded-full blur-[100px]" />
      <div className="absolute bottom-20 right-[10%] w-[350px] h-[350px] bg-gradient-to-r from-blue-100/20 to-violet-100/15 rounded-full blur-[100px]" />
      <div className="max-w-6xl mx-auto relative z-10">
        <StaggerContainer className="text-center mb-16">
          <StaggerItem><span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">About Us</span></StaggerItem>
          <StaggerItem><h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-neutral-900 mt-4">Built for the <GradientText>World</GradientText></h2></StaggerItem>
        </StaggerContainer>
        <div className="grid md:grid-cols-2 gap-10 items-center">
          <StaggerContainer>
            <StaggerItem><p className="text-lg text-neutral-500 mb-6 border-l-[3px] border-violet-400/60 pl-6">D23 AI is a WhatsApp-native AI assistant that breaks language barriers. We believe everyone deserves access to AI in the language they think in.</p></StaggerItem>
            <StaggerItem><p className="text-lg text-neutral-500 mb-6 border-l-[3px] border-violet-400/60 pl-6">Our mission is to make AI accessible to everyone, in their own language. Whether you speak Hindi, Tamil, Telugu, Bengali, or any of the 11+ languages we support, D23 AI understands and responds naturally.</p></StaggerItem>
            <StaggerItem><p className="text-lg text-neutral-500 border-l-[3px] border-violet-400/60 pl-6">From fact-checking viral messages to generating images, from playing games to getting instant answers — D23 AI is your intelligent companion on WhatsApp.</p></StaggerItem>
          </StaggerContainer>
          <StaggerItem>
            <TiltCard>
              <PremiumCard>
                <div className="p-8 space-y-6">
                  <div className="flex items-center gap-4"><div className="w-12 h-12 rounded-xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center"><Globe className="h-6 w-6 text-white" /></div><div><p className="text-2xl font-bold text-neutral-900">11+</p><p className="text-neutral-400">Languages Supported</p></div></div>
                  <div className="flex items-center gap-4"><div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-500 flex items-center justify-center"><MessageCircle className="h-6 w-6 text-white" /></div><div><p className="text-2xl font-bold text-neutral-900">WhatsApp</p><p className="text-neutral-400">Native Experience</p></div></div>
                  <div className="flex items-center gap-4"><div className="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center"><Zap className="h-6 w-6 text-white" /></div><div><p className="text-2xl font-bold text-neutral-900">&lt;2 Seconds</p><p className="text-neutral-400">Response Time</p></div></div>
                </div>
              </PremiumCard>
            </TiltCard>
          </StaggerItem>
        </div>
      </div>
    </section>
  )
}


// ============== SECURITY SECTION (NEW) ==============
function SecuritySection() {
  const t = useTranslations()

  const items = [
    { icon: <Lock className="h-7 w-7 text-white" />, color: "from-violet-500 to-purple-500", titleKey: "encryption", descKey: "encryptionDesc" },
    { icon: <ShieldCheck className="h-7 w-7 text-white" />, color: "from-indigo-500 to-blue-500", titleKey: "noDataSharing", descKey: "noDataSharingDesc" },
    { icon: <ShieldCheck className="h-7 w-7 text-white" />, color: "from-green-500 to-emerald-500", titleKey: "whatsappSecurity", descKey: "whatsappSecurityDesc" },
  ]

  return (
    <section className="py-24 px-6 bg-gradient-to-b from-violet-50/30 to-white">
      <div className="max-w-5xl mx-auto">
        <StaggerContainer className="text-center mb-20">
          <StaggerItem><span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">{t.security?.label ?? "Security"}</span></StaggerItem>
          <StaggerItem><h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mt-4">{t.security?.title ?? "Your privacy is"} <GradientText>{t.security?.titleHighlight ?? "our priority"}</GradientText></h2></StaggerItem>
        </StaggerContainer>
        <StaggerContainer className="grid md:grid-cols-3 gap-8">
          {items.map((item) => (
            <StaggerItem key={item.titleKey}>
              <motion.div whileHover={{ y: -4 }} className="group bg-white rounded-2xl p-10 border border-neutral-200/80 shadow-[0_1px_3px_rgba(0,0,0,0.04),0_6px_16px_rgba(0,0,0,0.06)] text-center hover:shadow-[0_2px_4px_rgba(0,0,0,0.04),0_12px_32px_rgba(0,0,0,0.08)] transition-all">
                <div className="relative inline-block mb-5">
                  <div className={cn("absolute inset-0 rounded-2xl blur-2xl opacity-20 group-hover:opacity-40 scale-150 transition-opacity bg-gradient-to-br", item.color)} />
                  <div className={cn("relative w-16 h-16 rounded-2xl bg-gradient-to-br flex items-center justify-center", item.color)}>
                    {item.icon}
                  </div>
                </div>
                <h3 className="text-xl font-semibold text-neutral-900 mb-3">{(t.security as any)?.[item.titleKey] ?? item.titleKey}</h3>
                <p className="text-neutral-500">{(t.security as any)?.[item.descKey] ?? item.descKey}</p>
              </motion.div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </section>
  )
}

// ============== FAQ SECTION ==============
function FAQSection() {
  const [open, setOpen] = useState<number | null>(null)
  const t = useTranslations()
  const faqIds = ["q1", "q2", "q3", "q4"] as const

  return (
    <section className="py-24 px-6">
      <div className="max-w-3xl mx-auto">
        <StaggerContainer className="text-center mb-16">
          <StaggerItem><span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">{t.faq.label}</span></StaggerItem>
          <StaggerItem><h2 className="text-3xl md:text-4xl lg:text-5xl font-bold text-neutral-900 mt-4">{t.faq.title} <GradientText>{t.faq.titleHighlight}</GradientText></h2></StaggerItem>
        </StaggerContainer>
        <StaggerContainer className="space-y-4">
          {faqIds.map((id, i) => (
            <StaggerItem key={id}>
              <div className={cn(
                "bg-white rounded-2xl overflow-hidden transition-all duration-300",
                open === i
                  ? "border border-violet-200 ring-1 ring-violet-100 shadow-[0_2px_4px_rgba(0,0,0,0.04),0_8px_24px_rgba(124,58,237,0.08)]"
                  : "border border-neutral-200 shadow-[0_1px_3px_rgba(0,0,0,0.04)]"
              )}>
                <button onClick={() => setOpen(open === i ? null : i)} className="w-full flex items-center gap-4 p-6 text-left">
                  <span className={cn(
                    "flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold transition-colors",
                    open === i ? "bg-violet-100 text-violet-600" : "bg-neutral-100 text-neutral-400"
                  )}>{i + 1}</span>
                  <span className="text-lg font-medium text-neutral-900 flex-1">{t.faq[id]}</span>
                  <motion.div animate={{ rotate: open === i ? 180 : 0 }} transition={{ duration: 0.3 }}><ChevronDown className="h-5 w-5 text-violet-500" /></motion.div>
                </button>
                <AnimatePresence>
                  {open === i && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }}>
                      <p className="px-6 pb-6 pl-[4.5rem] text-neutral-500">{t.faq[`a${i + 1}` as keyof typeof t.faq]}</p>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </StaggerItem>
          ))}
        </StaggerContainer>
      </div>
    </section>
  )
}

// ============== CONTACT SECTION ==============
function ContactSection() {
  return (
    <section id="contact" className="py-24 px-6 relative overflow-hidden">
      <div className="absolute top-10 right-[10%] w-[350px] h-[350px] bg-gradient-to-r from-violet-100/30 to-indigo-100/20 rounded-full blur-[100px]" />
      <div className="absolute bottom-10 left-[5%] w-[300px] h-[300px] bg-gradient-to-r from-blue-100/20 to-violet-100/15 rounded-full blur-[100px]" />
      <div className="max-w-4xl mx-auto relative z-10">
        <StaggerContainer className="text-center mb-16">
          <StaggerItem><span className="inline-flex items-center px-4 py-1.5 rounded-full bg-violet-100/80 border border-violet-200/60 text-violet-600 text-sm font-semibold tracking-wider uppercase">Contact</span></StaggerItem>
          <StaggerItem><h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mt-4">Get in <GradientText>Touch</GradientText></h2></StaggerItem>
          <StaggerItem><p className="text-neutral-500 mt-4 max-w-xl mx-auto">Have questions or feedback? We&apos;d love to hear from you. Reach out to us through any of these channels.</p></StaggerItem>
        </StaggerContainer>
        <StaggerContainer className="grid md:grid-cols-3 gap-6">
          <StaggerItem>
            <TiltCard className="h-full">
              <PremiumCard className="h-full">
                <div className="p-8 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-green-500 to-emerald-500 flex items-center justify-center mx-auto mb-4"><MessageCircle className="h-7 w-7 text-white" /></div>
                  <h3 className="text-lg font-semibold text-neutral-900 mb-2">WhatsApp</h3>
                  <p className="text-neutral-500 text-sm mb-4">Chat with D23 AI directly</p>
                  <Link href="https://wa.me/919934438606" target="_blank" className="text-violet-600 hover:text-violet-500 text-sm font-medium">+91 85488 19349</Link>
                </div>
              </PremiumCard>
            </TiltCard>
          </StaggerItem>
          <StaggerItem>
            <TiltCard className="h-full">
              <PremiumCard className="h-full">
                <div className="p-8 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-500 flex items-center justify-center mx-auto mb-4"><svg className="h-7 w-7 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/></svg></div>
                  <h3 className="text-lg font-semibold text-neutral-900 mb-2">Email</h3>
                  <p className="text-neutral-500 text-sm mb-4">For business inquiries</p>
                  <Link href="mailto:hello@d23.ai" className="text-violet-600 hover:text-violet-500 text-sm font-medium">hello@d23.ai</Link>
                </div>
              </PremiumCard>
            </TiltCard>
          </StaggerItem>
          <StaggerItem>
            <TiltCard className="h-full">
              <PremiumCard className="h-full">
                <div className="p-8 text-center">
                  <div className="w-14 h-14 rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-500 flex items-center justify-center mx-auto mb-4"><svg className="h-7 w-7 text-white" fill="currentColor" viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg></div>
                  <h3 className="text-lg font-semibold text-neutral-900 mb-2">Twitter/X</h3>
                  <p className="text-neutral-500 text-sm mb-4">Follow us for updates</p>
                  <Link href="https://twitter.com/D23AI" target="_blank" className="text-violet-600 hover:text-violet-500 text-sm font-medium">@D23AI</Link>
                </div>
              </PremiumCard>
            </TiltCard>
          </StaggerItem>
        </StaggerContainer>
      </div>
    </section>
  )
}

// ============== CTA SECTION (keep dark gradient for contrast) ==============
function CTASection() {
  const t = useTranslations()

  return (
    <section className="py-24 px-6">
      <div className="max-w-4xl mx-auto">
        <TiltCard>
          <div className="relative rounded-3xl overflow-hidden">
            <motion.div animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }} transition={{ duration: 10, repeat: Infinity, ease: "linear" }} className="absolute inset-0 bg-gradient-to-r from-violet-600 via-indigo-600 to-blue-600 bg-[length:200%_auto]" />
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[size:40px_40px]" />
            <div className="relative z-10 p-12 md:p-20 text-center">
              <motion.h2 initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} className="text-4xl md:text-5xl font-bold text-white mb-6">{t.cta.title}</motion.h2>
              <motion.p initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} viewport={{ once: true }} className="text-white/80 text-lg mb-10 max-w-xl mx-auto">{t.cta.subtitle}</motion.p>
              <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} viewport={{ once: true }} className="flex flex-wrap justify-center gap-4">
                <MagneticButton><Link href="https://wa.me/919934438606?text=Hey%20D23%20AI%21%20What%20can%20you%20do%3F" target="_blank" className="flex items-center gap-3 px-8 py-4 rounded-full bg-white text-violet-600 font-semibold shadow-2xl hover:bg-neutral-100 transition-colors"><MessageCircle className="h-5 w-5" />{t.cta.button1}</Link></MagneticButton>
                <MagneticButton><Link href="/chat" className="flex items-center gap-3 px-8 py-4 rounded-full border-2 border-white/30 text-white font-semibold hover:bg-white/10 transition-colors">{t.cta.button2}</Link></MagneticButton>
              </motion.div>
            </div>
          </div>
        </TiltCard>
      </div>
    </section>
  )
}

// ============== FOOTER ==============
function Footer() {
  const t = useTranslations()

  return (
    <footer className="py-12 px-6 border-t border-neutral-200">
      <div className="max-w-6xl mx-auto">
        <div className="relative rounded-3xl border border-neutral-200/80 bg-gradient-to-b from-neutral-50 to-white backdrop-blur-xl p-8 overflow-hidden shadow-[0_1px_3px_rgba(0,0,0,0.04),0_6px_16px_rgba(0,0,0,0.06)]">
          <div className="absolute top-0 left-1/4 w-64 h-64 bg-violet-100/50 rounded-full blur-3xl" />
          <div className="absolute bottom-0 right-1/4 w-64 h-64 bg-indigo-100/50 rounded-full blur-3xl" />
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <Image src="/d23ai-logo-v8.svg" alt="D23 AI" width={40} height={40} />
              <div><p className="text-lg font-bold text-neutral-900">D23 <GradientText>AI</GradientText></p><p className="text-sm text-neutral-400">{t.footer.tagline}</p></div>
            </div>
            <MagneticButton><Link href="https://wa.me/919934438606?text=Hey%20D23%20AI%21%20What%20can%20you%20do%3F" target="_blank" className="flex items-center gap-2 px-6 py-3 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 text-white font-medium shadow-lg shadow-violet-500/15">{t.footer.button}</Link></MagneticButton>
          </div>
          <div className="relative z-10 flex flex-col md:flex-row items-center justify-between gap-4 mt-8 pt-6 border-t border-neutral-200">
            <div className="flex items-center gap-4">
              {[{ icon: "X", href: "#" }, { icon: "IG", href: "#" }, { icon: "GH", href: "#" }].map((social) => (
                <Link key={social.icon} href={social.href} className="w-10 h-10 rounded-full bg-violet-50 border border-violet-200 flex items-center justify-center text-violet-500 hover:text-white hover:bg-gradient-to-r hover:from-violet-500 hover:to-indigo-500 hover:border-transparent transition-all text-xs font-bold">{social.icon}</Link>
              ))}
            </div>
            <p className="text-sm text-neutral-400">{t.footer.copyright}</p>
          </div>
        </div>
      </div>
    </footer>
  )
}

// ============== FLOATING WHATSAPP BUTTON (NEW) ==============
function FloatingWhatsAppButton() {
  return (
    <Link
      href="https://wa.me/919934438606?text=Hey%20D23%20AI%21%20What%20can%20you%20do%3F"
      target="_blank"
      className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-[#25D366] flex items-center justify-center shadow-lg shadow-green-500/30 hover:scale-110 transition-transform animate-pulse"
      aria-label="Chat on WhatsApp"
    >
      <svg className="w-7 h-7 text-white" fill="currentColor" viewBox="0 0 24 24">
        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
      </svg>
    </Link>
  )
}

// ============== PAGE CONTENT ==============
function PageContent() {
  const hydrated = useHydrated()

  if (!hydrated) {
    return (
      <div className="min-h-screen bg-white text-neutral-900 flex items-center justify-center">
        <div className="animate-pulse"><Image src="/d23ai-logo-v8.svg" alt="D23" width={80} height={80} priority /></div>
      </div>
    )
  }

  return (
    <div className="relative min-h-screen bg-white text-neutral-900 overflow-x-hidden">
      <div className="relative">
        <Header />
      </div>
      <main className="relative">
        <HeroSection />
        <LanguageMarquee />
        <SectionDivider />
        <HowItWorksSection />
        <SectionDivider />
        <AnimatedDemoShowcase />
        <FeaturesSection />
        <SectionDivider />
        <TestimonialsSection />
        <SectionDivider />
        <ComparisonSection />
        <SectionDivider />
        <AboutSection />
        <SectionDivider />
        <SecuritySection />
        <SectionDivider />
        <FAQSection />
        <SectionDivider />
        <ContactSection />
        <SectionDivider />
        <CTASection />
      </main>
      <Footer />
      <FloatingWhatsAppButton />
    </div>
  )
}

// ============== LANDING CONTENT PROVIDER ==============
function LandingContentProvider({ children }: { children: React.ReactNode }) {
  const [content, setContent] = useState<LandingContent>(defaultContent);

  useEffect(() => {
    const fetchContent = async () => {
      try {
        const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "https://api.d23.ai";
        const response = await fetch(`${apiBase}/admin/landing-content`);
        if (response.ok) {
          const data = await response.json();
          setContent(data);
        }
      } catch (error) {
        console.error("Failed to fetch landing content:", error);
      }
    };

    fetchContent();
  }, []);

  return (
    <LandingContentContext.Provider value={content}>
      {children}
    </LandingContentContext.Provider>
  );
}

// ============== MAIN PAGE ==============
export default function V7Page() {
  return (
    <LanguageProvider>
      <LandingContentProvider>
        <PageContent />
      </LandingContentProvider>
    </LanguageProvider>
  )
}
