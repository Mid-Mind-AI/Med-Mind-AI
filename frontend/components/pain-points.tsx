"use client";

import { motion } from "motion/react";
import { Clock, ClipboardList, UserX, AlertCircle } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";

const painPoints = [
  {
    icon: Clock,
    title: "Scheduling Inefficiencies",
    description: "Manual appointment booking leads to double-bookings, no-shows, and wasted time managing cancellations.",
  },
  {
    icon: ClipboardList,
    title: "Administrative Overload",
    description: "Staff spend hours on paperwork and data entry instead of focusing on patient care and support.",
  },
  {
    icon: UserX,
    title: "Limited Patient Context",
    description: "Doctors lack comprehensive patient information before visits, making it harder to provide effective care.",
  },
  {
    icon: AlertCircle,
    title: "Fragmented Systems",
    description: "Disconnected tools create data silos, making it difficult to access and share critical information.",
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

export function PainPoints() {
  return (
    <section className="w-full py-8 md:py-12 lg:py-16">
      <div className="container px-4 md:px-6 ">
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
            className="inline-block rounded-3xl bg-muted px-3 py-1 text-sm"
          >
            Current Challenges
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl"
          >
            The Healthcare Pain Points
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mx-auto max-w-[900px] text-muted-foreground md:text-xl/relaxed"
          >
            Many clinics struggle with outdated systems and manual processes that hinder efficiency and patient care
          </motion.p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="mx-auto grid max-w-5xl items-stretch gap-6 py-12 md:grid-cols-2 lg:grid-cols-4"
        >
          {painPoints.map((point, index) => (
            <motion.div key={index} variants={itemFadeIn} className="h-full">
              <Card className="relative h-full overflow-hidden border shadow-sm transition-all hover:shadow-md hover:border-primary/20 group bg-background/50 backdrop-blur-sm flex flex-col">
                <div className="absolute -right-20 -top-20 h-40 w-40 rounded-full bg-destructive/5 group-hover:bg-destructive/10 transition-all duration-300"></div>
                <CardContent className="relative p-6 space-y-4 flex-grow flex flex-col">
                  <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-destructive/10 to-destructive/5 flex items-center justify-center group-hover:scale-110 transition-transform">
                    <point.icon className="h-6 w-6 text-destructive" />
                  </div>
                  <h3 className="text-xl font-bold leading-tight">{point.title}</h3>
                  <p className="text-muted-foreground leading-relaxed flex-grow">{point.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}

