"use client";

import { motion } from "motion/react";
import { Calendar, Stethoscope, Shield, Zap, Activity, GitBranch } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const features = [
  {
    icon: Calendar,
    title: "Smart Booking Management",
    description: "AI-powered scheduling automatically optimizes appointments, sends reminders, and handles cancellations seamlessly.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Stethoscope,
    title: "AI Patient Insights",
    description: "Get comprehensive, AI-generated summaries of each patient's condition before visits for better preparation.",
    gradient: "from-purple-500 to-pink-500",
  },
  {
    icon: GitBranch,
    title: "EHR Integration",
    description: "Seamlessly sync with existing electronic health record systems without disrupting your workflow.",
    gradient: "from-green-500 to-emerald-500",
  },
  {
    icon: Zap,
    title: "Workflow Automation",
    description: "Automate administrative tasks to reduce paperwork and free up staff for patient-focused activities.",
    gradient: "from-orange-500 to-red-500",
  },
  {
    icon: Shield,
    title: "Enterprise-Grade Security",
    description: "Bank-level encryption with end-to-end security ensures complete patient data protection.",
    gradient: "from-indigo-500 to-purple-500",
  },
  {
    icon: Activity,
    title: "Real-time Analytics",
    description: "Track appointments, patient flow, and clinic performance with actionable insights and reporting.",
    gradient: "from-teal-500 to-cyan-500",
  },
];

const fadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6 },
  },
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
    },
  },
};

const itemFadeIn = {
  hidden: { opacity: 0, y: 20 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5 },
  },
};

export function Features() {
  return (
    <section className="w-full py-8 md:py-12 lg:py-16 bg-muted/20">
      <div className="container px-4 md:px-6 mx-auto">
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeIn}
          className="flex flex-col items-center justify-center space-y-4 text-center"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="inline-block rounded-3xl bg-background px-3 py-1 text-sm border"
          >
            Features
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl"
          >
            Everything You Need to Succeed
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mx-auto max-w-[900px] text-muted-foreground md:text-xl/relaxed"
          >
            Comprehensive tools designed to streamline your practice and enhance patient care
          </motion.p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="mx-auto grid max-w-5xl items-stretch gap-6 py-12 md:grid-cols-2 lg:grid-cols-3"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              variants={itemFadeIn}
              whileHover={{ y: -10, transition: { duration: 0.3 } }}
              className="h-full"
            >
              <Card className="relative overflow-hidden border shadow-sm transition-all hover:shadow-xl group bg-background/80 backdrop-blur-sm h-full flex flex-col">
                <div className={`absolute inset-0 bg-gradient-to-br ${feature.gradient} opacity-0 group-hover:opacity-5 transition-opacity duration-300`}></div>
                <div className={`absolute -right-20 -top-20 h-40 w-40 rounded-full bg-gradient-to-br ${feature.gradient} opacity-10 group-hover:opacity-20 transition-all duration-300`}></div>
                <CardContent className="relative p-6 space-y-4 flex-grow flex flex-col">
                  <div className={`h-12 w-12 rounded-2xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center group-hover:scale-110 transition-transform shadow-lg`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold leading-tight">{feature.title}</h3>
                  <p className="text-muted-foreground leading-relaxed flex-grow">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

