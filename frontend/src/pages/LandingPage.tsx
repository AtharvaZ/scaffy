import { Link } from 'react-router-dom';
import { Button } from '../components/ui/button';
import { DarkModeToggle } from '../components/DarkModeToggle';
import { EncryptedText } from '../components/ui/encrypted-text';
import { CodeBreakdownAnimation } from '../components/CodeBreakdownAnimation';

export function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-black">
      {/* Header */}
      <header className="border-b border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <Link to="/" className="flex items-center">
              <span className="text-[15px] font-semibold text-black dark:text-white">Scaffy</span>
            </Link>
            <div className="flex items-center gap-8">
              <DarkModeToggle />
              <Link to="/task">
                <Button size="sm" className="h-8 rounded-full bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 text-[13px] px-4 font-medium shadow-md shadow-blue-500/20">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-white dark:bg-black min-h-screen flex items-center">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8 w-full">
          <div className="mx-auto max-w-4xl text-center">
            <h1 className="text-[80px] leading-[1.1] font-bold tracking-[-0.04em]">
              <EncryptedText
                text="Learn programming."
                encryptedClassName="text-gray-400 dark:text-gray-600"
                revealedClassName="text-black dark:text-white"
                triggerOnHover={true}
              />
              <br />
              <EncryptedText
                text="Skip the struggle."
                encryptedClassName="text-gray-400 dark:text-gray-600"
                revealedClassName="bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-400 dark:to-blue-300 bg-clip-text text-transparent"
                triggerOnHover={true}
              />
            </h1>
            
            <p className="mt-6 text-xl text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
              AI-powered scaffolding breaks down assignments into tasks. Live execution catches errors. 
              Intelligent hints help you learn.
            </p>
            
            <div className="mt-10 flex items-center justify-center gap-3">
              <Link to="/task">
                <Button className="h-12 rounded-full bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 dark:from-blue-500 dark:to-blue-400 dark:hover:from-blue-600 dark:hover:to-blue-500 text-[15px] px-6 font-medium shadow-lg shadow-blue-500/30">
                  Start Building
                </Button>
              </Link>
            </div>
          </div>
        </div>

      </section>

      {/* Use Cases */}
      <section className="py-20 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Smart Scaffolding */}
            <div className="group relative rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-300 hover:border-blue-500/70 dark:hover:border-blue-400/70 hover:shadow-[0_0_50px_rgba(59,130,246,0.6),inset_0_0_0_1px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_0_50px_rgba(59,130,246,0.5),inset_0_0_0_1px_rgba(59,130,246,0.3)] hover:scale-[1.02]">
              <div className="mb-8">
                <span className="text-2xl">📝</span>
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                Smart Scaffolding
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Break down complex assignments into manageable tasks with AI-powered guidance and syntax hints.
              </p>
            </div>

            {/* Live Execution */}
            <div className="group relative rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-300 hover:border-blue-500/70 dark:hover:border-blue-400/70 hover:shadow-[0_0_50px_rgba(59,130,246,0.6),inset_0_0_0_1px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_0_50px_rgba(59,130,246,0.5),inset_0_0_0_1px_rgba(59,130,246,0.3)] hover:scale-[1.02]">
              <div className="mb-8">
                <span className="text-2xl">⚡</span>
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                Live Execution
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Compile and run code in real-time. Get instant feedback on errors and test results as you type.
              </p>
            </div>

            {/* AI Guidance */}
            <div className="group relative rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-300 hover:border-blue-500/70 dark:hover:border-blue-400/70 hover:shadow-[0_0_50px_rgba(59,130,246,0.6),inset_0_0_0_1px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_0_50px_rgba(59,130,246,0.5),inset_0_0_0_1px_rgba(59,130,246,0.3)] hover:scale-[1.02]">
              <div className="mb-8">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="text-lg font-semibold mb-2 text-foreground">
                AI Guidance
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Progressive hints that adapt to your pace. Learn concepts deeply, don't just copy code.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Code Breakdown Animation */}
      <section className="py-20 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-[48px] leading-[1.1] font-bold tracking-[-0.02em] mb-4">
              <span className="text-black dark:text-white">Break down </span>
              <span className="bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-400 dark:to-blue-300 bg-clip-text text-transparent">complex code</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Watch how Scaffy transforms overwhelming assignments into manageable tasks
            </p>
          </div>
          <div className="max-w-5xl mx-auto">
            <CodeBreakdownAnimation />
          </div>
        </div>
      </section>

      {/* Your product, delivered */}
      <section className="py-20 bg-gray-50/50 dark:bg-gray-900/20">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-[48px] leading-[1.1] font-bold tracking-[-0.02em] mb-4">
              <span className="text-black dark:text-white">Your learning, </span>
              <span className="bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-400 dark:to-blue-300 bg-clip-text text-transparent">accelerated.</span>
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              While ChatGPT generates code, Scaffy compiles it, runs it, and explains your specific errors.
            </p>
          </div>

          {/* Feature showcase */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="group relative rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-300 hover:border-blue-500/70 dark:hover:border-blue-400/70 hover:shadow-[0_0_50px_rgba(59,130,246,0.6),inset_0_0_0_1px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_0_50px_rgba(59,130,246,0.5),inset_0_0_0_1px_rgba(59,130,246,0.3)] hover:scale-[1.02]">
              <div className="font-mono text-xs text-muted-foreground mb-4">STEP 1</div>
              <h3 className="text-xl font-semibold mb-3 text-foreground">
                Assignment Breakdown
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Upload your assignment and watch as AI breaks it into clear, manageable tasks with syntax guidance for your target language.
              </p>
            </div>

            <div className="group relative rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-300 hover:border-blue-500/70 dark:hover:border-blue-400/70 hover:shadow-[0_0_50px_rgba(59,130,246,0.6),inset_0_0_0_1px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_0_50px_rgba(59,130,246,0.5),inset_0_0_0_1px_rgba(59,130,246,0.3)] hover:scale-[1.02]">
              <div className="font-mono text-xs text-muted-foreground mb-4">STEP 2</div>
              <h3 className="text-xl font-semibold mb-3 text-foreground">
                Real-Time Feedback
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Write code and see compilation errors instantly. Run tests to validate your solution without leaving the editor.
              </p>
            </div>

            <div className="group relative rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-300 hover:border-blue-500/70 dark:hover:border-blue-400/70 hover:shadow-[0_0_50px_rgba(59,130,246,0.6),inset_0_0_0_1px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_0_50px_rgba(59,130,246,0.5),inset_0_0_0_1px_rgba(59,130,246,0.3)] hover:scale-[1.02]">
              <div className="font-mono text-xs text-muted-foreground mb-4">STEP 3</div>
              <h3 className="text-xl font-semibold mb-3 text-foreground">
                Intelligent Hints
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Stuck? Get progressive hints that adapt to your attempts. Learn the 'why' behind solutions, not just the 'how'.
              </p>
            </div>

            <div className="group relative rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-6 shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] dark:shadow-[inset_0_0_0_1px_rgba(255,255,255,0.05)] transition-all duration-300 hover:border-blue-500/70 dark:hover:border-blue-400/70 hover:shadow-[0_0_50px_rgba(59,130,246,0.6),inset_0_0_0_1px_rgba(59,130,246,0.3)] dark:hover:shadow-[0_0_50px_rgba(59,130,246,0.5),inset_0_0_0_1px_rgba(59,130,246,0.3)] hover:scale-[1.02]">
              <div className="font-mono text-xs text-muted-foreground mb-4">STEP 4</div>
              <h3 className="text-xl font-semibold mb-3 text-foreground">
                Track Progress
              </h3>
              <p className="text-sm text-muted-foreground leading-relaxed">
                Monitor concept mastery as you code. Build confidence as you complete tasks and understand new patterns.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Comparison Section */}
      <section className="py-20 border-t border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-[48px] leading-[1.1] font-bold tracking-[-0.02em] text-black dark:text-white mb-4">
              The Scaffy Difference
            </h2>
            <p className="text-lg text-gray-600 dark:text-gray-400">
              Traditional learning vs. the Scaffy approach
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Without Scaffy */}
            <div className="rounded-2xl border border-gray-300/50 dark:border-gray-700/50 bg-card p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-red-100 dark:bg-red-900/20 mb-3">
                  <span className="text-red-600 dark:text-red-400">✕</span>
                </div>
                <h3 className="text-xl font-bold text-black dark:text-white">Without Scaffy</h3>
              </div>
              <ul className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>Overwhelming assignments with no clear starting point</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>Hours debugging syntax errors in unfamiliar languages</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>Copy-paste from AI without understanding</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500 mt-1">•</span>
                  <span>No feedback until final submission</span>
                </li>
              </ul>
            </div>

            {/* With Scaffy */}
            <div className="rounded-2xl border border-blue-300/50 dark:border-blue-700/50 bg-gradient-to-br from-blue-50/50 to-white dark:from-blue-900/10 dark:to-black p-8">
              <div className="text-center mb-6">
                <div className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900/20 mb-3">
                  <span className="text-blue-600 dark:text-blue-400">✓</span>
                </div>
                <h3 className="text-xl font-bold text-black dark:text-white">With Scaffy</h3>
              </div>
              <ul className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>Clear breakdown into manageable tasks</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>Instant compilation feedback as you type</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>Progressive hints that promote understanding</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-blue-500 mt-1">•</span>
                  <span>Real-time test validation and error explanations</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-32 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8">
          <div className="text-center">
            <h2 className="text-[56px] leading-[1.1] font-bold tracking-[-0.02em] mb-6">
              <span className="text-black dark:text-white">Start building </span>
              <span className="bg-gradient-to-r from-blue-600 to-blue-400 dark:from-blue-400 dark:to-blue-300 bg-clip-text text-transparent">today.</span>
            </h2>
            <div className="flex items-center justify-center gap-3">
              <Link to="/task">
                <Button className="h-12 rounded-full bg-gradient-to-r from-blue-600 to-blue-500 text-white hover:from-blue-700 hover:to-blue-600 dark:from-blue-500 dark:to-blue-400 dark:hover:from-blue-600 dark:hover:to-blue-500 text-[15px] px-6 font-medium shadow-lg shadow-blue-500/30">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200/60 dark:border-gray-800/60 bg-white dark:bg-black">
        <div className="mx-auto max-w-[1440px] px-6 lg:px-8 py-12">
          <div className="flex items-center justify-between">
            <p className="text-xs text-gray-600 dark:text-gray-400">
              © 2025 Scaffy
            </p>
            <div className="flex items-center gap-6">
              <span className="text-xs text-gray-600 dark:text-gray-400">Built for students learning programming</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

