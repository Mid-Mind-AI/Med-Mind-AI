import Image from "next/image";
import { Hero } from "@/components/hero";
import { PainPoints } from "@/components/pain-points";
import { Features } from "@/components/features";
import { About } from "@/components/about";
import FAQs from "@/components/faq";
import HoverFooter from "@/components/hover-footer";

export default function Home() {
  return (
    <div className="flex flex-col bg-linear-to-b from-background to-secondary/90">
      <div className="flex flex-col mx-auto">
        <Hero />
        <PainPoints />
        <Features />
        <About />
        <FAQs />
        <HoverFooter />
      </div>
    </div>
  );
}
