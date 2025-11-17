"use client";

import { FingerprintIcon, Menu, Moon, Sun } from "lucide-react";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";

import { Button } from "@/components/ui/button";
import { motion } from "motion/react";
import { SimpleHeader } from "./simple-header";


export function Hero() {
  return (
      <div className="container max-w-5xl mx-auto">


        <main className="relative container px-2 mx-auto">
          <section className="w-full py-8 sm:py-12 md:py-20 lg:py-28 xl:py-36">
            <motion.div
              className="flex flex-col items-center space-y-4 sm:space-y-6 text-center"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
            >
              <motion.h1
                className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl xl:text-7xl/none px-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2, duration: 0.5 }}
              >
                Intelligent Healthcare,{" "}
                <span className="bg-gradient-to-r from-primary to-purple-500 bg-clip-text text-transparent">
                  Simplified
                </span>
              </motion.h1>
              <motion.p
                className="mx-auto max-w-xl text-base sm:text-lg md:text-xl lg:text-2xl text-muted-foreground px-4 leading-relaxed"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3, duration: 0.5 }}
              >
                AI-powered booking management and{" "}
                <span className="font-semibold text-foreground">
                  patient insights
                </span>{" "}
                to transform{" "}
                <span className="font-semibold text-foreground">your practice</span>
              </motion.p>
              <motion.div
                className="flex flex-col sm:flex-row gap-3 sm:gap-4 w-full sm:w-auto px-4"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4, duration: 0.5 }}
              >
                <Button className="rounded-xl bg-foreground text-background hover:bg-foreground/90 w-full sm:w-auto">
                  Get Started
                  <div className="ml-2 space-x-1 hidden sm:inline-flex">
                    <FingerprintIcon className="w-5 h-5" />
                  </div>
                </Button>
                <Button variant="outline" className="rounded-xl w-full sm:w-auto">
                  <div className="mr-2 space-x-1 hidden sm:inline-flex">
                    <span className="w-5 h-5 text-xs rounded-sm border">⌘</span>
                    <span className="w-5 h-5 text-xs rounded-sm border">B</span>
                  </div>
                  Watch Demo
                </Button>
              </motion.div>

              <motion.div
                className="flex flex-col items-center space-y-3 sm:space-y-4 pb-8 sm:pb-12 px-4 w-full"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5, duration: 0.5 }}
              >
                <div className="flex flex-wrap items-center justify-center gap-x-3 gap-y-1 sm:gap-x-4 text-xs sm:text-sm px-2">
                  <span className="text-primary hover:text-primary/80 transition-colors whitespace-nowrap">
                    Enterprise-Grade Security
                  </span>
                  <span className="text-muted-foreground/40 hidden sm:inline">•</span>
                  <span className="text-muted-foreground/60 whitespace-nowrap">
                    Secure & Private
                  </span>
                  <span className="text-muted-foreground/40 hidden sm:inline">•</span>
                  <span className="text-primary hover:text-primary/80 transition-colors whitespace-nowrap">
                    AI-Powered
                  </span>
                </div>
                <p className="text-xs sm:text-sm text-muted-foreground/60 text-center px-4 max-w-md">
                  Built for healthcare professionals who care about their patients
                </p>
              </motion.div>
              <motion.div
                className="w-full border p-1.5 sm:p-2 rounded-2xl sm:rounded-3xl mx-4 sm:mx-0"
                initial={{ opacity: 0, y: 40 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6, duration: 0.8 }}
              >
                <div className="relative w-full">
                  <div className="relative w-full rounded-2xl sm:rounded-3xl overflow-hidden border shadow-xl sm:shadow-2xl">
                    <img
                      src="https://ui.shadcn.com/examples/dashboard-dark.png"
                      alt="Dashboard Preview"
                      className="w-full h-auto object-center hidden dark:block rounded-2xl sm:rounded-3xl"
                    />
                    <img
                      src="https://ui.shadcn.com/examples/dashboard-light.png"
                      alt="Dashboard Preview"
                      className="w-full h-auto object-center dark:hidden block rounded-2xl sm:rounded-3xl"
                    />
                  </div>
                  <div className="absolute inset-x-0 bottom-0 h-[50%] bg-gradient-to-t from-background to-transparent" />
                </div>
              </motion.div>
            </motion.div>
          </section>
        </main>
      </div>
  );
}
