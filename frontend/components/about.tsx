"use client";

import { motion } from "motion/react";
import { Heart, Target, Award } from "lucide-react";

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

export function About() {
  return (
    <section className="w-full py-8 md:py-12 lg:py-16">
      <div className="container px-4 md:px-6">
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
            About Us
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl"
          >
            Empowering Healthcare Excellence
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mx-auto max-w-[900px] text-muted-foreground md:text-xl/relaxed"
          >
            We're committed to transforming healthcare through intelligent, secure, and reliable AI technology
          </motion.p>
        </motion.div>

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          className="mx-auto grid max-w-5xl gap-8 py-12 md:grid-cols-3"
        >
          <motion.div
            variants={itemFadeIn}
            whileHover={{ y: -10 }}
            className="flex flex-col items-center text-center space-y-4 p-8 rounded-3xl border bg-background/50 backdrop-blur-sm hover:shadow-lg transition-all"
          >
            <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center">
              <Heart className="h-8 w-8 text-primary" />
            </div>
            <h3 className="text-2xl font-bold">Our Mission</h3>
            <p className="text-muted-foreground">
              To empower healthcare professionals with cutting-edge AI solutions that enhance patient care and streamline operations
            </p>
          </motion.div>

          <motion.div
            variants={itemFadeIn}
            whileHover={{ y: -10 }}
            className="flex flex-col items-center text-center space-y-4 p-8 rounded-3xl border bg-background/50 backdrop-blur-sm hover:shadow-lg transition-all"
          >
            <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-purple-500/10 to-purple-500/5 flex items-center justify-center">
              <Target className="h-8 w-8 text-purple-500" />
            </div>
            <h3 className="text-2xl font-bold">Our Vision</h3>
            <p className="text-muted-foreground">
              A world where technology seamlessly supports healthcare providers, enabling them to focus on what matters most: their patients
            </p>
          </motion.div>

          <motion.div
            variants={itemFadeIn}
            whileHover={{ y: -10 }}
            className="flex flex-col items-center text-center space-y-4 p-8 rounded-3xl border bg-background/50 backdrop-blur-sm hover:shadow-lg transition-all"
          >
            <div className="h-16 w-16 rounded-2xl bg-gradient-to-br from-blue-500/10 to-blue-500/5 flex items-center justify-center">
              <Award className="h-8 w-8 text-blue-500" />
            </div>
            <h3 className="text-2xl font-bold">Our Values</h3>
            <p className="text-muted-foreground">
              Innovation, accuracy, security, and trust are at the core of everything we build for the healthcare community
            </p>
          </motion.div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.8 }}
          className="mt-16 mx-auto max-w-3xl rounded-3xl border bg-gradient-to-br from-background to-muted/30 p-8 md:p-12 text-center"
        >
          <h3 className="text-2xl md:text-3xl font-bold mb-4">
            Built for Healthcare Professionals
          </h3>
          <p className="text-muted-foreground md:text-lg">
            Our team combines deep medical expertise with cutting-edge AI technology to create solutions that truly understand the challenges of modern healthcare practices. We're not just building software—we're building a better future for patient care.
          </p>
        </motion.div>
      </div>
    </section>
  );
}

