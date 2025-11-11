"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { ChevronDown, Shield, Lock, Plug, Clock, HelpCircle } from "lucide-react";

const faqs = [
  {
    icon: Shield,
    question: "What security measures does AIPPA use?",
    answer: "AIPPA employs enterprise-grade security measures including bank-level encryption for data at rest and in transit, multi-factor authentication, strict access controls, and comprehensive audit logging. All data is stored in secure cloud infrastructure with redundant backups and disaster recovery protocols. We prioritize patient data protection through industry-standard security practices.",
  },
  {
    icon: Lock,
    question: "How secure is patient data?",
    answer: "Security is our top priority. We use bank-level encryption for data at rest and in transit, implement multi-factor authentication, and maintain strict audit logs. All data is stored in secure, compliant cloud infrastructure with redundant backups and disaster recovery protocols.",
  },
  {
    icon: Plug,
    question: "Does it integrate with our existing EHR system?",
    answer: "Yes, AIPPA integrates seamlessly with major EHR systems including Epic, Cerner, Allscripts, and more. Our flexible API architecture ensures smooth data synchronization without disrupting your current workflow. Setup typically takes less than a day.",
  },
  {
    icon: Clock,
    question: "How long does implementation take?",
    answer: "Most clinics are up and running within 1-2 weeks. Our onboarding team handles the entire setup process, including EHR integration, staff training, and configuration. We provide 24/7 support during the transition period to ensure a smooth implementation.",
  },
  {
    icon: HelpCircle,
    question: "How easy is it to learn and use?",
    answer: "Extremely easy. Our intuitive interface requires minimal training—most staff members are productive within their first day. We provide comprehensive documentation, video tutorials, and dedicated support to help your team succeed. No technical expertise required.",
  },
  {
    icon: Shield,
    question: "What about downtime and technical support?",
    answer: "We guarantee 99.9% uptime with redundant systems and cloud infrastructure. Our support team is available 24/7 via phone, email, and live chat to resolve any issues quickly. We also offer proactive monitoring to prevent problems before they occur.",
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

interface FAQItemProps {
  faq: typeof faqs[0];
  index: number;
  isOpen: boolean;
  onToggle: () => void;
}

function FAQItem({ faq, isOpen, onToggle }: FAQItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      className="border rounded-3xl overflow-hidden bg-background/50 backdrop-blur-sm hover:shadow-md transition-all"
    >
      <button
        onClick={onToggle}
        className="w-full p-6 flex items-center justify-between text-left group hover:bg-muted/50 transition-colors"
      >
        <div className="flex items-center gap-4 flex-1">
          <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-primary/10 to-primary/5 flex items-center justify-center flex-shrink-0">
            <faq.icon className="h-6 w-6 text-primary" />
          </div>
          <span className="font-semibold text-lg pr-8 group-hover:text-primary transition-colors">
            {faq.question}
          </span>
        </div>
        <motion.div
          animate={{ rotate: isOpen ? 180 : 0 }}
          transition={{ duration: 0.3 }}
          className="flex-shrink-0"
        >
          <ChevronDown className="h-5 w-5 text-muted-foreground group-hover:text-primary transition-colors" />
        </motion.div>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="overflow-hidden"
          >
            <div className="px-6 pb-6 pl-24 text-muted-foreground">
              {faq.answer}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

export function FAQ() {
  const [openIndex, setOpenIndex] = useState<number | null>(null);

  const toggleFAQ = (index: number) => {
    setOpenIndex(openIndex === index ? null : index);
  };

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
            className="inline-block rounded-3xl bg-background px-3 py-1 text-sm border"
          >
            FAQ
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl"
          >
            Frequently Asked Questions
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mx-auto max-w-[900px] text-muted-foreground md:text-xl/relaxed"
          >
            Everything you need to know about AIPPA and how it can transform your practice
          </motion.p>
        </motion.div>

        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={fadeIn}
          className="mx-auto max-w-4xl py-12 space-y-4"
        >
          {faqs.map((faq, index) => (
            <FAQItem
              key={index}
              faq={faq}
              index={index}
              isOpen={openIndex === index}
              onToggle={() => toggleFAQ(index)}
            />
          ))}
        </motion.div>
      </div>
    </section>
  );
}

