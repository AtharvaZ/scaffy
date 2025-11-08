import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { DarkModeToggle } from '../components/DarkModeToggle';
import { Code2, Zap, CheckCircle2, ArrowRight } from 'lucide-react';
import PixelBlast from '../components/PixelBlast';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-background relative">
      {/* PixelBlast Full Page Background - Component inspired by github.com/zavalit/bayer-dithering-webgl-demo */}
      <div 
        className="fixed inset-0 -z-10"
        style={{ 
          width: '100vw', 
          height: '100vh'
        }}
      >
        <PixelBlast
          variant="circle"
          pixelSize={6}
          color="#B19EEF"
          patternScale={3}
          patternDensity={1.2}
          pixelSizeJitter={0.5}
          enableRipples
          rippleSpeed={0.4}
          rippleThickness={0.12}
          rippleIntensityScale={1.5}
          liquid
          liquidStrength={0.12}
          liquidRadius={1.2}
          liquidWobbleSpeed={5}
          speed={0.6}
          edgeFade={0.25}
          transparent
          style={{ width: '100%', height: '100%' }}
        />
      </div>
      
      {/* Header */}
      <header className="border-b border-black/5 dark:border-border">
        <div className="mx-auto max-w-7xl px-6 sm:px-8 lg:px-12">
          <div className="flex h-16 items-center justify-between">
            <h1 className="text-xl font-semibold tracking-tight text-black dark:text-foreground">Scaffy</h1>
            <div className="flex items-center gap-3">
              <DarkModeToggle />
              <Link to="/task">
                <Button variant="outline" size="sm">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative mx-auto max-w-7xl px-6 py-24 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-3xl text-center relative z-10">
          <h2 className="text-5xl font-semibold tracking-tight text-black dark:text-foreground sm:text-6xl">
            Learn New Programming Languages
            <span className="block text-gray-600 dark:text-muted-foreground">Without Getting Stuck</span>
          </h2>
          <p className="mt-6 text-lg leading-8 text-gray-600 dark:text-muted-foreground">
            Break down complex assignments into manageable tasks with real-time compilation feedback, 
            instant test validation, and AI-powered guidance.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <Link to="/task">
              <Button size="lg" className="bg-black text-white hover:bg-black/90 dark:bg-primary dark:text-primary-foreground dark:hover:bg-primary/90">
                Start Learning
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-2xl">
          <div className="rounded-lg border border-black/5 dark:border-border bg-gray-50 dark:bg-card p-8 vercel-shadow">
            <h3 className="text-2xl font-semibold tracking-tight text-black dark:text-foreground mb-4">
              The Problem
            </h3>
            <p className="text-gray-700 dark:text-muted-foreground leading-relaxed">
              Students learning new programming languages face dense assignments requiring both 
              complex logic <strong>AND</strong> unfamiliar syntax. They either copy from AI without 
              learning or give up entirely.
            </p>
          </div>
        </div>
      </section>

      {/* Solution Section */}
      <section className="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-2xl">
          <h3 className="text-2xl font-semibold tracking-tight text-black dark:text-foreground mb-8 text-center">
            Our Solution
          </h3>
          <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-8 vercel-shadow">
            <p className="text-gray-700 dark:text-muted-foreground leading-relaxed mb-4">
              <strong>Assignment Scaffolder PLUS Live Execution Engine</strong> - Not only breaks 
              down assignments into manageable tasks with syntax guidance, but also provides:
            </p>
            <ul className="space-y-3 text-gray-700 dark:text-muted-foreground">
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-black dark:text-foreground mt-0.5 flex-shrink-0" />
                <span>Real-time compilation feedback</span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-black dark:text-foreground mt-0.5 flex-shrink-0" />
                <span>Instant test validation</span>
              </li>
              <li className="flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-black dark:text-foreground mt-0.5 flex-shrink-0" />
                <span>Concept mastery tracking as students code</span>
              </li>
            </ul>
            <div className="mt-6 p-4 bg-black/5 dark:bg-muted rounded-md">
              <p className="text-sm font-medium text-black dark:text-foreground">
                The Killer Addition:
              </p>
              <p className="text-sm text-gray-700 dark:text-muted-foreground mt-1">
                While ChatGPT can generate code, it can't compile it, run it, or tell you 
                <strong> WHY</strong> your specific error happened. <strong>We can.</strong>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-5xl">
          <h3 className="text-2xl font-semibold tracking-tight text-black dark:text-foreground mb-12 text-center">
            Features
          </h3>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-6 vercel-shadow">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-black dark:bg-primary">
                <Code2 className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-lg font-semibold text-black dark:text-foreground mb-2">Smart Scaffolding</h4>
              <p className="text-sm text-gray-600 dark:text-muted-foreground">
                Break down complex assignments into manageable, step-by-step tasks with syntax guidance.
              </p>
            </div>
            <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-6 vercel-shadow">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-black dark:bg-primary">
                <Zap className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-lg font-semibold text-black dark:text-foreground mb-2">Live Execution</h4>
              <p className="text-sm text-gray-600 dark:text-muted-foreground">
                Compile and run your code in real-time with instant feedback on errors and test results.
              </p>
            </div>
            <div className="rounded-lg border border-black/5 dark:border-border bg-white dark:bg-card p-6 vercel-shadow">
              <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-black dark:bg-primary">
                <CheckCircle2 className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-lg font-semibold text-black dark:text-foreground mb-2">AI Guidance</h4>
              <p className="text-sm text-gray-600 dark:text-muted-foreground">
                Get progressive hints and explanations that adapt to your learning pace and attempts.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="mx-auto max-w-7xl px-6 py-16 sm:px-8 lg:px-12">
        <div className="mx-auto max-w-2xl text-center">
          <h3 className="text-2xl font-semibold tracking-tight text-black dark:text-foreground mb-4">
            Ready to Start Learning?
          </h3>
          <p className="text-gray-600 dark:text-muted-foreground mb-8">
            Experience the future of programming education with real-time feedback and AI-powered guidance.
          </p>
          <Link to="/task">
            <Button size="lg" className="bg-black text-white hover:bg-black/90 dark:bg-primary dark:text-primary-foreground dark:hover:bg-primary/90">
              Get Started
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-black/5 dark:border-border mt-24">
        <div className="mx-auto max-w-7xl px-6 py-12 sm:px-8 lg:px-12">
          <p className="text-center text-sm text-gray-600 dark:text-muted-foreground">
            © 2024 Scaffy. Built for students learning new programming languages.
          </p>
        </div>
      </footer>
    </div>
  );
}

