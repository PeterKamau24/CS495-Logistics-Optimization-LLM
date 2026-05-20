# Speaker Notes — Branch & Bound Capstone Presentation

What to say at the podium for each slide. Total target: **~7 minutes**, leaving
3 minutes for questions.

---

## Pre-talk (30 seconds before you start)

- Have the presentation in fullscreen (press `F` in reveal.js).
- Speaker notes pop-up: press `S`. Use it on a second monitor if you have one.
- Glance at the wall clock — write the target end time on your notepad.
- Take a breath. Smile. Say your opening sentence in your head.

---

## Slide 1 — Title (20s)

> "Good morning. My name is Peter Kamau, this is my CS495 capstone with
> Prof. Dr. Pedro Albuquerque. The project is about integer optimization for
> logistics — and today I'm going to show you the algorithm that's powering it
> under the hood, called Branch and Bound. I implemented it in three languages
> — Python, C++, and x86-64 Assembly — so we can separate two questions that
> usually get tangled up: *does the algorithm matter, or does the language
> matter?* The answer is both, but not by the same amount."

**Transition:** "Let me start with the problem itself."

---

## Slide 2 — The 0-1 Knapsack Problem (30s)

> "This is the canonical knapsack problem. You have n items, each with a weight
> and a value, and a knapsack of capacity C. You pick a subset — every item is
> either in or out, that's the 'zero-one' part — that maximizes total value
> without exceeding capacity. It's NP-hard, meaning we don't know a polynomial
> algorithm that solves it exactly in the worst case."

**Point at the right column.**

> "Why does this matter for logistics? My capstone's production problem is
> driver-to-region assignment — every driver is either assigned to a region or
> not, every assignment has a cost, and you have eligibility constraints.
> **Same structure.** Binary decisions, linear objective, linear constraints.
> And every industrial solver — CBC, Gurobi, CPLEX — uses Branch and Bound
> under the hood."

**Transition:** "Let me show you a concrete tiny example."

---

## Slide 3 — A Concrete Tiny Instance (30s)

> "Four items, capacity 8. I've sorted them by value-per-weight ratio,
> descending — that's important and I'll come back to it. At n=4 there are 16
> possible subsets, you could enumerate them by hand. But at n=25 — which is
> still tiny — that's 33 million subsets. Hold this example in your head,
> because in two slides we'll walk the actual Branch and Bound tree on this
> exact instance."

**Sotto voce, for those who care:** "The optimum here is B plus C — value 22,
weight 8."

**Transition:** "First, the baseline. The dumbest thing that works."

---

## Slide 4 — Baseline: Brute Force (30s)

> "Brute force is one loop. Iterate over every bitmask from zero to 2^n minus
> one — that's every possible subset — and keep the best feasible one. It's
> correct, it's trivial, and it scales like the number of atoms in a small
> galaxy."

**Tap the screen.**

> "The complexity is **O(2^n)** time, **O(1)** extra memory. Every new item
> doubles the work. This is the wall."

**Transition:** "Here's what that exponential actually looks like, across three
languages."

---

## Slide 5 — Brute Force: Python vs C++ vs ASM (45s)  *[NEW PLOT]*

> "Same six instances — n equals three to twenty-five — three languages.
> **Y-axis is log scale, seconds.** Read the slope, not the heights."

**Sweep your hand left to right.**

> "Every step up in n is roughly an order of magnitude — that's 2^n in
> disguise. The constant factor between languages is real — Assembly is about
> twenty times faster than Python at n=25 — but the *shape* is identical. All
> three lines have the same slope. **Language choice is a constant factor. The
> exponential is not.**"

**The punchline:**

> "At n=25, Python takes 102 seconds. C++ takes 15. Assembly takes about 5.
> So the question is — what happens at n=30, or n=40? In Python, n=30 is 30
> minutes. n=40 is half a year. You cannot out-engineer 2^n. You need a
> smarter algorithm."

**Transition:** "That smarter algorithm is Branch and Bound."

---

## Slide 6 — Branch and Bound — The Idea (30s)

> "Three words. **Branch, bound, prune.** Branch means: at each item, recurse
> on include versus exclude — exactly the same decision tree as brute force.
> Bound means: at every node, compute an upper bound on the best value the
> subtree could possibly produce. Prune means: if that upper bound is no better
> than the best solution you already have, **skip the subtree entirely.**"

**Pause for a beat.**

> "It's just informed DFS. The cleverness is in two things — the bound has to
> be valid and cheap, and the search order matters. I'll show you both."

**Transition:** "Here's the tree on our four-item example."

---

## Slide 7 — Decision Tree Picture (60s)  *[BIGGEST PEDAGOGICAL SLIDE]*

**Stand back, let the audience read for two seconds.**

> "OK. Sixteen possible subsets, we explore nine nodes. Walk it left to right
> with me."

**Point at the root.**

> "Root: nothing picked yet, LP-relaxation bound is 27.2 — that's the *best
> case* if we could take fractional items."

**Move to A=1.**

> "We descend include-first. Include A — value 10, weight 2. Include B — value
> 20, weight 5. Now we try include C, but C weighs 5 and we only have 3 left.
> **Infeasible.** Orange node. We back up, exclude C, descend D — same
> problem. We back up and we have value 20 in hand."

**Move to the right subtree.**

> "Now we exclude A from the root. Include B, include C — value 22, weight 8.
> **Feasible.** Green node — this is our best, the incumbent."

**Point at the red nodes.**

> "From here on, look at the red. These subtrees have LP bounds less than or
> equal to 22 — we *know* they cannot beat what we already have, so we cut
> them off. **Nine nodes touched out of sixteen.** At n=25, the ratio is closer
> to a thousand-to-one."

**The key insight:**

> "The reason this works is that we sorted by value-per-weight ratio. The
> include-first descent follows the greedy choice, which means we find a
> strong incumbent *fast*, which makes the bound condition fire *early*.
> **Sorting is not cosmetic — it's the engine of the pruning.**"

**Transition:** "Let me show you what the bound actually is."

---

## Slide 8 — The Bound: LP Relaxation (45s)

> "Branch and Bound needs a bound function. Mine is the LP relaxation —
> meaning, relax the binary constraint, let xᵢ be any value between 0 and 1.
> The fractional knapsack has a *closed-form greedy solution*: walk the
> remaining items in ratio order, take each whole, and take a fraction of
> whatever item first overflows the capacity."

**Tap the code.**

> "Because the items are already sorted, this is **one O(n) sweep, no LP
> solver needed.** And the integer floor of this bound is still a valid bound
> for integer solutions — which is why my Assembly version stays entirely in
> integer registers. No floating point. Just `idiv`."

**Transition:** "And here's why I did this in three languages."

---

## Slide 9 — Same Algorithm, Three Languages (30s)

> "Same recursion. Same prune-then-branch order. Same include-before-exclude
> descent. Python and C++ are line-for-line equivalent. The Assembly version
> follows the Windows x64 ABI — r12 and r13 hold pointers to the sorted
> weights and values, ebx holds the running incumbent, and recursion uses
> `call` and `ret` on the real call stack. The bound is computed inline in
> integer division."

**The methodological point:**

> "Same algorithm in three implementations is a **controlled experiment.**
> Any timing difference is now language overhead, not algorithm difference."

**Transition:** "Here's the result."

---

## Slide 10 — Branch and Bound: Python vs C++ vs ASM (45s)  *[NEW PLOT]*

> "Same six instances. Same three languages. Same machine. **Look at the
> y-axis. Microseconds. Not seconds.**"

**Compare to the previous plot mentally.**

> "Brute force at n=25 in Python was 102 seconds. Branch and Bound at n=25 in
> Python is 98 microseconds. The relative language ordering is preserved —
> Assembly beats C++ beats Python by roughly the same constant factors. But
> the y-axis has dropped by *six orders of magnitude*."

**The clean takeaway:**

> "This is what I wanted to show. **Algorithm and language are orthogonal axes.
> They multiply, they don't interact.** The algorithm win is six orders of
> magnitude. The language win is one. Both matter, but the algorithm
> dominates."

**Transition:** "Now — why is this relevant to a logistics capstone?"

---

## Slide 11 — Connection to My Capstone (30s)

**Point left.**

> "The production track is a binary integer linear program — assign drivers
> to regions, minimize cost, respect eligibility. I model it with PuLP, and
> PuLP hands it to **CBC, which is a Branch and Bound solver**. The algorithm
> I just walked you through is the *same family* as what's actually solving
> my production problem. Knapsack is the didactic sibling."

**Point right.**

> "On the LLM track — knapsack is the perfect testbed. It's small, it's
> well-defined, and I have ground truth from this hand-built work. When I ask
> an LLM to write a knapsack solver, I can *measure* whether it produced
> Branch and Bound or just brute force."

**Transition:** "Here's the architecture in one picture."

---

## Slide 12 — Where B&B Fits in the Capstone (30s)

**Trace the top row.**

> "Top — production. CSV in, preprocessing, PuLP model, CBC solver,
> assignments out."

**Trace the bottom row.**

> "Bottom — this work. Knapsack instances feed two **independent** benchmark
> tracks: brute force on top, branch and bound on bottom. Three languages
> each."

**Point at the dashed red line.**

> "And the link in the middle — CBC and my hand-built Branch and Bound are
> the *same algorithm family*. That's the reason this isn't a side quest.
> **I'm studying the engine I'm depending on.**"

**Transition:** "Three takeaways, then questions."

---

## Slide 13 — Takeaways (30s)

> "Three things to leave you with."

**Beat 1.**

> "**Algorithm choice dominates language choice.** Six orders of magnitude
> from Branch and Bound versus one order from Assembly. Get the algorithm
> right first."

**Beat 2.**

> "**Same algorithm in three languages is a controlled experiment.** It
> cleanly separates the two dimensions. Neither factor masked the other."

**Beat 3.**

> "**This is the engine of the tools I'm using.** PuLP, CBC, Gurobi — they
> all sit on top of Branch and Bound. Mastering knapsack means understanding
> what's happening when I write `prob.solve()`."

**End on confidence.**

> "Thank you. Happy to take questions."

---

## Anticipated Q&A — prep these answers cold

**Q: Why not dynamic programming?**

> "DP is pseudo-polynomial — O(n × C) in capacity. It's fantastic when
> capacity is small, and in fact I use it as a verification cross-check in the
> test suite. But for the LP-ILP connection I wanted to study, B&B is the
> right algorithm — it's what CBC is doing."

**Q: Why Assembly? Isn't that overkill?**

> "Two reasons. One — it quantifies the *ceiling*. ASM is what you get when
> nothing is in your way. That gives me a clean upper bound on what
> hand-tuning is worth. Two — the capstone has a three-language comparison
> angle, and ASM is the most informative bottom end. Whether you'd maintain
> ASM in production is a separate question — and the answer is usually no."

**Q: What's the LP relaxation actually doing here?**

> "It's solving a *fractional* knapsack — same items, but you can take half
> an item. That has a closed-form greedy solution when items are sorted by
> value-to-weight ratio. The relaxed optimum is always at least as large as
> the integer optimum, so it's a valid upper bound. And because the
> relaxation is tight, the bound prunes aggressively."

**Q: Does this scale to your production instance?**

> "The driver-region instance is small — four drivers, three regions — and
> CBC solves it in milliseconds. Where this work pays off is in
> *understanding* what CBC is doing, so when I scale to a real fleet I'll
> know what knobs to turn — cuts, heuristics, warm starts."

**Q: How did you verify correctness across the three languages?**

> "Every implementation returns the optimal value, and I cross-checked
> against (a) the brute-force baseline on small instances, (b) PuLP/CBC as an
> independent reference, and (c) a pytest suite that runs the canonical
> instances. All three languages return the same optima."

**Q: Why didn't you compare B&B against brute force in a single chart?**

> "Deliberate choice. They're different algorithms with different asymptotic
> complexities and the comparison is, in some sense, unfair — you'd be
> measuring milliseconds against minutes. The cleaner story is to present
> each algorithm on its own and let the y-axis units do the comparison.
> That's what the two plots do — log seconds for brute force, microseconds
> for B&B."

---

## Delivery tips

- **Don't read your slides.** The audience can read. Your job is to add
  *what's not on the slide* — the why, the intuition, the connection.
- **Pause after big claims.** "Six orders of magnitude" deserves a one-second
  pause.
- **Look at the audience, not the screen.** Glance at the screen only to
  point.
- **If you blank: go to the next slide.** Don't apologize, don't backtrack.
  Forward motion.
- **Time check at slide 7.** If you're past 3:30, speed up the bound slide.
  If you're under 3:00, slow down the decision tree.
- **End on time. End on time. End on time.** Stopping at 7:00 with one minute
  of buffer is better than rushing the takeaways.

Good luck. You know this material — your job at the podium is to let the
audience see that you know it.
