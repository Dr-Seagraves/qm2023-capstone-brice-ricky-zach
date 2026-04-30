# Individual Addendum - Brice

**Name:** Brice  
**Team:** Brice, Ricky, Zach  
**Date:** May 1, 2026

---

## 1. Personal Contribution to Capstone Milestones

### Milestone 1: Data Pipeline (Week 5)
- Developed research question: "How do repeated natural disasters affect local housing price growth and volatility in high-risk counties?" Posted to discussion board and conducted literature survey
- Formulated 3 preliminary hypotheses grounded in economic theory (repair-cost channel, insurance-risk premium channel, credit/affordability channel)
- Designed initial data architecture: identified NOAA Storm Events, Shiller HPI, and FRED as data sources; specified outcome (yoy_real), drivers (event_count, total_damage), and controls (mortgage_rate, unemployment)
- Coordinated team task allocation for M1: assigned Zach to pipeline construction, Ricky to verification and documentation
- Hours: 12 hours
- Key deliverable: Research question and 3-hypothesis framework; data source specification in README.md

### Milestone 2: EDA Dashboard (Week 10)
- Refined hypotheses based on M2 findings: documented how M2 lag analysis and group sensitivity results would inform M3 specification
- Led hypothesis-to-specification translation: wrote "Hypotheses for M3" section of M2_EDA_summary.md, mapping correlation results to econometric model choices (FE, lagged variables, group interactions)
- Contributed to scenario analysis: identified rate-sensitive regions (Midwest, South, West) and discussed policy implications for regional housing markets
- Synthesized data quality flags for downstream modeling: articulated which issues (outlier periods, missing values, heteroskedasticity) would require robustness checks in M3
- Hours: 10 hours
- Key deliverable: M2 hypothesis refinement and specification guidance for M3

### Milestone 3: Econometric Models (Week 12)
- Reviewed M3 model specifications with team: confirmed FE + lagged disasters aligned with M2 hypotheses; discussed identification challenges (national outcome × county predictors)
- Interpreted economic meaning of near-zero coefficients: translated statistical insignificance into economic findings ("disasters do not appear to be the dominant driver")
- Prepared economic reasoning for M3 interpretation: documented the three expected theory channels and honestly explained why they were not supported in this panel
- Updated `AI_AUDIT_APPENDIX.md` (M3 section): ensured all modeling trade-offs and limitations were transparently documented
- Hours: 8 hours
- Key deliverable: M3 economic interpretation, theory-channel discussion, honest caveats

### Milestone 4: Final Investment Memo (Week 14)
- Drafted Executive Summary: stated key finding ("no meaningful disaster-price penalty"), provided investment recommendation ("treat disaster history as secondary risk screen, focus on rate-sensitive markets first")
- Drafted framing memo headings and structural logic: ensured Executive Summary → Methodology → Results → Recommendations flow was logical and compelling
- Strategic recommendations writing: translated null FE results into actionable guidance (rate awareness, market positioning, risk assessment)
- Coordinated memo integration: solicited Ricky's methodology/conclusions edits, verified Zach's table/figure formatting, created final polished executive summary
- Hours: 12 hours
- Key deliverable: Executive Summary, Investment Recommendations, overall memo narrative arc

**Total Hours:** 42 hours

---

## 2. One Defended Methodological Decision

**Decision:** Frame the research question around repeated disaster *exposure* (event count, cumulative damage) rather than disaster *timing* or *seasonality*, and intentionally use a national housing outcome (Shiller HPI) rather than pursue county-level indices

**Reasoning:**
- Evidence: M2 showed no strong within-county seasonal pattern in yoy_real; variation is dominated by national macro cycles (2005 spike, 2008 crash). This suggested that county-level timing of disasters is dwarfed by national rate environment.
- Economic justification: For an investment committee, the relevant question is "how much should I weight disaster history in my allocation?" If the answer is "very little relative to interest rates," that is economically important. Using a national outcome and county FE isolates the county-level residual shock from disasters after removing national trends—a conservative test of disaster pricing.
- Robustness support: M3 robustness checks confirmed that lags 1, 2, 3 all show coefficients near zero (and even more insignificant as lag increases). This robustness across lags validates the frame: if disasters mattered, some lag would show a significant effect.

**Alternative considered:** Use Case-Shiller zip-code level indices (post-1987 only) to create truly local outcomes
- Why not: Would cut the panel to 35 years, lose 40+ years of historical data, and introduce additional missing data for rural zips. The trade-off favored the national panel even with the identification caveat.

---

## 3. One Key Limitation of Our Analysis

**Limitation:** Our research question assumes that disaster effects on housing markets operate through county-level mechanisms (local repair costs, insurance premia, risk perceptions). However, national mortgage rates dominate housing growth variation, and our model absorbs all national variation with year fixed effects. This leaves very little cross-county variation to identify disaster effects, making the "no effect" finding potentially an artifact of weak identification rather than a true null.

**Why this matters:** If the true disaster effect is small but real (e.g., −2% annually in repeat-loss counties), our panel design might not have enough power to detect it. An investment committee relying on this memo might incorrectly ignore disaster history entirely, when they should treat it as a secondary screen (risk management, operational resilience) even if it is not a primary pricing signal.

**Potential mitigation:** Conduct a subsample analysis restricting to periods of low rate volatility (1985–1995, 2003–2007) where year FE does not absorb as much variation. Alternatively, use a dynamic specification (lagged dependent variable) or a structural break model to test whether disaster effects have changed over time. Future work with true local price indices (FHFA, repeat-sales) would be definitive.

---

## 4. AI Audit — Detailed Examples

### Example 1: Research Question Formulation
- **Prompt:** "I have a capstone project on climate disasters and housing. What is the key economic question I should answer? Give me 3 research questions with increasing specificity."
- **Output:** Three nested questions (general → specific → specific with mechanism)
- **Verification:** Reviewed questions against existing REIT/disaster literature; confirmed the final question ("How do repeated disasters affect local housing growth?") was novel and grounded in economic theory; discussed with team before finalizing
- **Critique:** AI's first draft was overly broad ("Do disasters affect real estate?"). I narrowed it to "repeated disasters" (not one-off events) and "housing price growth" (not volatility), making the research question tractable and policy-relevant.

### Example 2: Investment Recommendation Wording
- **Prompt:** "How do I translate 'statistically insignificant FE coefficient' into a recommendation for a portfolio manager?"
- **Output:** Template recommending using macro conditions as primary screen
- **Verification:** Sent draft recommendation to team for sense-check; verified recommendation was not overstated (did not say "ignore disasters") but appropriately cautious (treat as secondary screen); confirmed it matched both the statistical and economic evidence
- **Critique:** AI's first version was too timid. I sharpened it to "treat disaster history as a secondary risk screen, not a primary pricing signal," which is honest but actionable.

### Example 3: Theory Channel Discussion
- **Prompt:** "We found no disaster effect. What are the three mechanisms by which disasters *should* affect housing prices according to economic theory? How do I explain why we didn't find evidence?"
- **Output:** Three channels (repair costs, insurance risk, credit conditions); discussion of why panel design is weak identification
- **Verification:** Cross-checked channels against paper titles in housing/disaster literature; confirmed they were the mainstream hypotheses; verified that the explanation (national outcome × county FE absorbs variation) was correctly stated
- **Critique:** AI initially suggested that our result means "disasters don't matter," which is too strong. I rewrote to "disasters do not appear to be the dominant driver in this panel," reserving the possibility that a better identification strategy would uncover effects.

### Overall AI Use
**Estimate:** Approximately 15% of my work involved AI assistance (primarily brainstorming research questions and recommendation phrasing). All hypothesis development, economic reasoning, and investment recommendations were my independent work. AI helped me articulate ideas but did not generate the core intellectual content.

**Types of help:** Brainstorming questions, writing scaffolding for recommendations, translating econometrics to business language
**What I verified independently:** Every recommendation was grounded in M3 results and M2 findings. All economic claims passed a "would an investment committee buy this logic?" test before inclusion in the memo.

---

## 5. Self-Reflection

### What did I do particularly well on this capstone?
I excelled at connecting the empirical findings to real-world investment implications. Translating "coefficient near zero, p = 0.789" into "treat disaster history as secondary risk screen" is the core value I added. I also did well framing the project from the start—investing time early in a thoughtful research question paid dividends throughout M2–M4.

### What could I have improved?
I could have engaged more deeply with the econometric execution in M3. Knowing the limitations of our design earlier (national outcome, county FE) might have prompted us to explore alternative outcomes faster. I also could have done more literature review on disaster-housing links to defend or adjust expectations heading into M3.

### What did I learn from this capstone project?
I learned that a rigorous "no effect" finding is often more valuable than a flashy positive result if it is backed by robust methods and honest limitations. I also learned to lead with research design rather than chase interesting findings—the investment memo was much stronger once we committed to the FE specification and stuck with it even when results were null. Finally, I developed confidence in translating between academic econometrics and practitioner language, which I expect will be a valuable skill in consulting or asset management.

---

## 6. Attestation

By submitting this individual addendum, I affirm that:
- ☑ All contributions listed above are accurate and honest
- ☑ I have not exaggerated my role or minimized teammates' contributions
- ☑ I understand this addendum may be used to adjust my individual grade relative to the team grade
- ☑ I take full responsibility for my work and any errors in the sections I authored

**Signature:** _________________________________ **Date:** May 1, 2026
