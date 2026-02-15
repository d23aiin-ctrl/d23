"use client"

import Image from "next/image"
import Link from "next/link"
import { motion } from "framer-motion"
import {
  Sparkles, Zap, Heart, Globe, Users, Target, MessageCircle,
  ArrowRight, Linkedin, Mail
} from "lucide-react"
import { cn } from "@/lib/utils"

// Gradient Text Component
function GradientText({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return (
    <span className={cn(
      "bg-gradient-to-r from-violet-600 via-indigo-500 to-blue-500 bg-clip-text text-transparent",
      className
    )}>
      {children}
    </span>
  )
}

// Header Component
function Header() {
  return (
    <header
      className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-xl border-b border-neutral-200/80"
      style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.04)' }}
    >
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
            <Image src="/d23-logo-icon.png" alt="D23" width={40} height={40} />
            <span className="text-xl font-bold">D23 <GradientText>AI</GradientText></span>
          </Link>

          <nav className="hidden md:flex items-center gap-8">
            {["Integrations", "MCP", "Contact"].map((item) => (
              <Link
                key={item}
                href={`/${item.toLowerCase()}`}
                className="text-sm text-neutral-500 hover:text-neutral-900 transition-colors"
              >
                {item}
              </Link>
            ))}
          </nav>

          <Link
            href="https://wa.me/919934438606?text=Hey%20D23%20AI%21%20What%20can%20you%20do%3F"
            target="_blank"
            className="flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-violet-600 to-indigo-600 text-white text-sm font-medium"
          >
            <Zap className="h-4 w-4" />
            Try Now
          </Link>
        </div>
      </div>
    </header>
  )
}

// Team Members - Founders
const team = [
  {
    name: "Naseer",
    role: "Co-Founder & CEO",
    linkedin: "#",
    image: null
  },
  {
    name: "Pawan",
    role: "Co-Founder & CPO",
    linkedin: "https://www.linkedin.com/in/pawan-k-singh-119b8a20/",
    image: "/puch/team/pawan.jpeg"
  },
  {
    name: "Rishi",
    role: "Co-Founder & CTO",
    linkedin: "https://www.linkedin.com/in/rishi-kumar-5878742a/",
    image: "/puch/team/rishi.png"
  }
]

// Developers Team
const developers = [
  {
    name: "Manoj",
    role: "Developer",
    linkedin: "https://www.linkedin.com/in/manoj-kaushik-0a81b5246/",
    image: "/puch/team/manoj.jpeg"
  },
  {
    name: "Nikhil",
    role: "Developer",
    linkedin: "https://www.linkedin.com/in/nikhil-kumar-765b14237",
    image: "/puch/team/nikhil.jpeg"
  },
  {
    name: "Amit",
    role: "Developer",
    linkedin: "#",
    image: "/puch/team/amit.jpg"
  }
]

// Values
const values = [
  {
    icon: Globe,
    title: "Accessible AI",
    description: "Making AI available to everyone, regardless of language or technical expertise.",
    color: "from-violet-500 to-purple-500"
  },
  {
    icon: Heart,
    title: "Built for Everyone",
    description: "Designed for users everywhere with support for 11+ languages.",
    color: "from-fuchsia-500 to-pink-500"
  },
  {
    icon: Users,
    title: "User First",
    description: "Every feature is designed with our users' needs and feedback in mind.",
    color: "from-cyan-500 to-blue-500"
  },
  {
    icon: Target,
    title: "Continuous Innovation",
    description: "Constantly improving and adding new capabilities based on user needs.",
    color: "from-orange-500 to-red-500"
  }
]

// Stats
const stats = [
  { value: "5000+", label: "Active Users" },
  { value: "11+", label: "Languages" },
  { value: "1M+", label: "Messages" },
  { value: "24/7", label: "Available" }
]

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-white text-neutral-900 overflow-x-hidden">
      <Header />

      {/* Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-blue-100/20 rounded-full blur-[120px]" />
        <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-amber-100/15 rounded-full blur-[120px]" />
        <div className="absolute top-1/2 right-1/3 w-[400px] h-[400px] bg-sky-100/15 rounded-full blur-[120px]" />
        <div className="absolute inset-0 bg-[linear-gradient(rgba(0,0,0,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(0,0,0,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />
      </div>

      <main className="relative z-10">
        {/* Hero */}
        <section className="pt-32 pb-20 px-6">
          <div className="max-w-5xl mx-auto text-center">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="mb-8"
            >
              <Image
                src="/d23-logo-icon.png"
                alt="D23 AI Logo"
                width={120}
                height={120}
                className="mx-auto"
              />
            </motion.div>

            <motion.h1
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-4xl md:text-5xl lg:text-6xl font-bold text-neutral-900 mb-6"
            >
              We are on a <GradientText>mission</GradientText>
              <br />
              to make AI accessible to everyone
            </motion.h1>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="text-lg md:text-xl text-neutral-600 max-w-3xl mx-auto"
            >
              D23 AI is building the future of multilingual conversational AI.
              We believe everyone deserves access to powerful AI tools in their own language.
            </motion.p>
          </div>
        </section>

        {/* Stats */}
        <section className="py-12 px-6 border-y border-neutral-200">
          <div className="max-w-5xl mx-auto">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, i) => (
                <motion.div
                  key={stat.label}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  viewport={{ once: true }}
                  className="text-center"
                >
                  <div className="text-3xl md:text-4xl font-bold text-neutral-900 mb-1">
                    <GradientText>{stat.value}</GradientText>
                  </div>
                  <div className="text-sm text-neutral-500">{stat.label}</div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* Mission */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <span className="text-neutral-600 text-sm font-semibold tracking-wider uppercase">Our Story</span>
              <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mt-3">
                Why we built <GradientText>D23 AI</GradientText>
              </h2>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="space-y-6 text-lg text-neutral-600 leading-relaxed"
            >
              <p>
                The world is home to thousands of languages.
                Yet, most AI tools are built primarily for English speakers, leaving a vast majority behind.
              </p>
              <p>
                We started D23 AI with a simple belief: <span className="text-neutral-900 font-medium">AI should speak your language</span>.
                Whether you're a farmer asking about weather, a student seeking homework help,
                or a shopkeeper checking train timings -- D23 AI is here to help.
              </p>
              <p>
                Built on WhatsApp -- the world's most popular messaging app -- D23 AI brings the power of advanced AI to your fingertips,
                in Hindi, Tamil, Telugu, Bengali, Marathi, Gujarati, and many more languages.
              </p>
            </motion.div>
          </div>
        </section>

        {/* Values */}
        <section className="py-20 px-6">
          <div className="max-w-6xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <span className="text-neutral-600 text-sm font-semibold tracking-wider uppercase">Our Values</span>
              <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mt-3">
                What drives us
              </h2>
            </motion.div>

            <div className="grid md:grid-cols-2 gap-6">
              {values.map((value, i) => {
                const Icon = value.icon
                return (
                  <motion.div
                    key={value.title}
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    transition={{ delay: i * 0.1 }}
                    viewport={{ once: true }}
                    className="bg-white rounded-2xl border border-neutral-200/80 p-6 hover:border-neutral-300 hover:shadow-lg transition-all"
                    style={{ boxShadow: '0 1px 3px rgba(0,0,0,0.04), 0 6px 16px rgba(0,0,0,0.06)' }}
                  >
                    <div className={cn(
                      "w-14 h-14 rounded-xl flex items-center justify-center mb-4 bg-gradient-to-br",
                      value.color
                    )}>
                      <Icon className="h-7 w-7 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-neutral-900 mb-2">{value.title}</h3>
                    <p className="text-neutral-600">{value.description}</p>
                  </motion.div>
                )
              })}
            </div>
          </div>
        </section>

        {/* Team */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <span className="text-neutral-600 text-sm font-semibold tracking-wider uppercase">Our Team</span>
              <h2 className="text-3xl md:text-4xl font-bold text-neutral-900 mt-3">
                Meet the founders
              </h2>
            </motion.div>

            <div className="flex flex-wrap justify-center gap-12">
              {team.map((member, i) => (
                <motion.div
                  key={member.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  viewport={{ once: true }}
                  className="text-center"
                >
                  <div className="relative w-32 h-32 mx-auto mb-4">
                    <div className="absolute inset-0 rounded-full bg-gradient-to-r from-violet-300 to-indigo-300 blur-md opacity-40" />
                    {member.image ? (
                      <Image
                        src={member.image}
                        alt={member.name}
                        width={128}
                        height={128}
                        className="relative w-32 h-32 rounded-full object-cover border-2 border-neutral-300"
                      />
                    ) : (
                      <div className="relative w-32 h-32 rounded-full bg-neutral-100 flex items-center justify-center border-2 border-neutral-300">
                        <span className="text-4xl font-bold text-neutral-900">{member.name[0]}</span>
                      </div>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-neutral-900">{member.name}</h3>
                  <p className="text-sm text-neutral-500 mb-3">{member.role}</p>
                  <a
                    href={member.linkedin}
                    className="w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-500 hover:text-neutral-900 hover:bg-neutral-200 transition-colors mx-auto"
                  >
                    <Linkedin className="h-4 w-4" />
                  </a>
                </motion.div>
              ))}
            </div>

            {/* Developers Section */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="text-center mt-20 mb-12"
            >
              <span className="text-neutral-600 text-sm font-semibold tracking-wider uppercase">Development Team</span>
              <h3 className="text-2xl md:text-3xl font-bold text-neutral-900 mt-3">
                Meet the developers
              </h3>
            </motion.div>

            <div className="flex flex-wrap justify-center gap-10">
              {developers.map((dev, i) => (
                <motion.div
                  key={dev.name}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  viewport={{ once: true }}
                  className="text-center"
                >
                  <div className="relative w-24 h-24 mx-auto mb-4">
                    <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-300 to-blue-300 blur-md opacity-30" />
                    {dev.image ? (
                      <Image
                        src={dev.image}
                        alt={dev.name}
                        width={96}
                        height={96}
                        className="relative w-24 h-24 rounded-full object-cover border-2 border-neutral-300"
                      />
                    ) : (
                      <div className="relative w-24 h-24 rounded-full bg-neutral-100 flex items-center justify-center border-2 border-neutral-300">
                        <span className="text-3xl font-bold text-neutral-900">{dev.name[0]}</span>
                      </div>
                    )}
                  </div>
                  <h3 className="text-lg font-semibold text-neutral-900">{dev.name}</h3>
                  <p className="text-sm text-neutral-500 mb-3">{dev.role}</p>
                  <a
                    href={dev.linkedin}
                    className="w-8 h-8 rounded-full bg-neutral-100 flex items-center justify-center text-neutral-500 hover:text-neutral-900 hover:bg-neutral-200 transition-colors mx-auto"
                  >
                    <Linkedin className="h-4 w-4" />
                  </a>
                </motion.div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA - stays dark for contrast */}
        <section className="py-20 px-6">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="relative rounded-3xl overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-violet-600 via-purple-600 to-fuchsia-600" />
              <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[size:40px_40px]" />

              <div className="relative z-10 p-12 md:p-20 text-center">
                <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                  Ready to try D23 AI?
                </h2>
                <p className="text-white/80 text-lg mb-8 max-w-xl mx-auto">
                  Join thousands of users worldwide using AI in their own language.
                </p>

                <Link
                  href="https://wa.me/919934438606?text=Hey%20D23%20AI%21%20What%20can%20you%20do%3F"
                  target="_blank"
                  className="inline-flex items-center gap-2 px-8 py-4 rounded-full bg-white text-violet-600 font-semibold shadow-2xl hover:bg-neutral-50 transition-colors"
                >
                  <MessageCircle className="h-5 w-5" />
                  Start Chatting
                  <ArrowRight className="h-5 w-5" />
                </Link>
              </div>
            </motion.div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative z-10 py-12 px-6 border-t border-neutral-200">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-3">
              <Image src="/d23-logo-icon.png" alt="D23 AI" width={40} height={40} />
              <div>
                <p className="text-lg font-bold text-neutral-900">D23 <GradientText>AI</GradientText></p>
                <p className="text-sm text-neutral-400">Your multilingual WhatsApp AI.</p>
              </div>
            </div>
            <p className="text-sm text-neutral-400">&copy; 2026 D23 AI. Built for every language.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}
