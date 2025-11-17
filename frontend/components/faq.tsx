"use client";

import Link from "next/link";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";

const faqItems = [
  {
    id: "security-measures",
    question: "What security measures does AIPPA use?",
    answer: "AIPPA employs enterprise-grade security measures including bank-level encryption for data at rest and in transit, multi-factor authentication, strict access controls, and comprehensive audit logging. All data is stored in secure cloud infrastructure with redundant backups and disaster recovery protocols. We prioritize patient data protection through industry-standard security practices.",
  },
  {
    id: "patient-data-security",
    question: "How secure is patient data?",
    answer: "Security is our top priority. We use bank-level encryption for data at rest and in transit, implement multi-factor authentication, and maintain strict audit logs. All data is stored in secure, compliant cloud infrastructure with redundant backups and disaster recovery protocols.",
  },
  {
    id: "ehr-integration",
    question: "Does it integrate with our existing EHR system?",
    answer: "Yes, AIPPA integrates seamlessly with major EHR systems including Epic, Cerner, Allscripts, and more. Our flexible API architecture ensures smooth data synchronization without disrupting your current workflow. Setup typically takes less than a day.",
  },
  {
    id: "implementation-time",
    question: "How long does implementation take?",
    answer: "Most clinics are up and running within 1-2 weeks. Our onboarding team handles the entire setup process, including EHR integration, staff training, and configuration. We provide 24/7 support during the transition period to ensure a smooth implementation.",
  },
  {
    id: "ease-of-use",
    question: "How easy is it to learn and use?",
    answer: "Extremely easy. Our intuitive interface requires minimal training—most staff members are productive within their first day. We provide comprehensive documentation, video tutorials, and dedicated support to help your team succeed. No technical expertise required.",
  },
  {
    id: "downtime-support",
    question: "What about downtime and technical support?",
    answer: "We guarantee 99.9% uptime with redundant systems and cloud infrastructure. Our support team is available 24/7 via phone, email, and live chat to resolve any issues quickly. We also offer proactive monitoring to prevent problems before they occur.",
  },
];

export default function FAQs() {
  return (
    <section className="py-16 md:py-24 lg:py-32">
      <div className="mx-auto max-w-5xl px-4 md:px-6">
        <div className="mx-auto max-w-2xl text-center space-y-3 mb-16">
          <h2 className="text-balance text-3xl font-bold tracking-tight md:text-4xl lg:text-5xl">
            Frequently Asked Questions
          </h2>
          <p className="text-muted-foreground text-base md:text-lg leading-relaxed max-w-xl mx-auto">
            Discover quick and comprehensive answers to common questions about our platform, services, and features.
          </p>
        </div>

        <div className="mx-auto max-w-2xl">
          <Accordion
            type="single"
            collapsible
            className="bg-card w-full rounded-2xl border shadow-sm hover:shadow-md transition-shadow duration-300"
          >
            {faqItems.map((item, index) => (
              <AccordionItem
                key={item.id}
                value={item.id}
                className="border-b last:border-b-0 px-6 md:px-8 first:pt-4 last:pb-4"
              >
                <AccordionTrigger className="cursor-pointer text-base md:text-lg font-semibold hover:no-underline py-5 hover:text-primary transition-colors duration-200 group data-[state=open]:text-primary">
                  <span className="text-left pr-4 leading-relaxed">{item.question}</span>
                </AccordionTrigger>
                <AccordionContent className="pb-5">
                  <p className="text-base md:text-[15px] text-muted-foreground leading-relaxed pr-4">
                    {item.answer}
                  </p>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>

          <p className="text-muted-foreground mt-8 text-center text-sm md:text-base">
            Can't find what you're looking for?{" "}
            <Link
              href="#"
              className="text-primary font-medium hover:underline underline-offset-4 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 rounded-sm"
            >
              Contact our customer support team
            </Link>
          </p>
        </div>
      </div>
    </section>
  );
}

