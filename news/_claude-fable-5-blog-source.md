# Claude Fable 5 — Anthropic zdejmuje blokadę. Pierwszy publiczny Mythos

**Data:** 2026-06-09 · **Źródła:** Anthropic, The Verge, TechCrunch, CNBC, VentureBeat, SecurityWeek, AWS, Anthropic docs · **Czas czytania:** ~4 min

---

## Co się stało

Anthropic 9 czerwca 2026 wydał **Claude Fable 5** ($10/$50 za M tokenów) — pierwszy model klasy Mythos dopuszczony do publicznego użytku. Razem z nim wypuszczono **Claude Mythos 5** (ten sam model, częściowo zdjęte safety guards, tylko dla Project Glasswing partnerów). To dual-release: Fable 5 + Mythos 5 = ten sam model, dwa opakowania.

## Kluczowe liczby

- **$10/$50** — cena Fable 5 per M tokenów (input/output). 2× drożej od Opus 4.8 ($5/$25), 5× taniej od wycofanego Mythos Preview ($20/$100).
- **80.3%** — SWE-Bench Pro (agentic coding). vs GPT-5.5 58.6%, Gemini 3.1 Pro 54.2%. Dwudziestodwupunktowa przepaść w kodowaniu.
- **29.3%** — FrontierCode Diamond xhigh. 2× lepiej od Opus 4.8 (13.4%), 5× lepiej od GPT-5.5 (5.7%).
- **1932 ELO** — GDPval-AA (knowledge work). vs Opus 4.8 1890, GPT-5.5 1769, Gemini 3.1 Pro 1314.
- **85.0%** — OSWorld-Verified (computer use). Marginalnie za Mythos Preview (85.4%).
- **1M / 128K** — context window (input / output).
- **<5%** — odsetek sesji Fable 5 triggerujących safety classifier (95% pure Fable).
- **30 dni** — mandatory retention dla Mythos-class traffic, NIE używane do treningu.
- **22 czerwca** — deadline darmowego dostępu w claude.ai Pro/Max/Team/Enterprise.
- **15** — liczba krajów w Project Glasswing (z hundreds of organizations).

## Dlaczego "Fable"

Anthropic przeskoczył z **Opus 4.8** (maj 2026) bezpośrednio do **Fable 5** — nie ma Fable 1-4. "Fable" (bajka) sygnalizuje **Mythos-class, ale bezpieczny dla ogólnego użytku**. To celowy pivot brandingowy po tym, jak w czerwcu branża dyskutowała o "AI too dangerous to release". Fable = opowieść/narracja, nie cyberweapon.

## Sandwich architektura

Gdy Fable 5 classifier wykryje zapytanie z high-risk domeny (cyber, bio, chem, distillation), **cicho przekierowuje do Opus 4.8**. Użytkownik może nawet nie wiedzieć, który model odpowiedział.

Trzy chronione domeny:
1. **Cybersecurity** — exploitation, offensive cyber, agentic hacking → fallback do Opus 4.8
2. **Biology & chemistry** — over-broad (planowane zwężenie dla legit biomedical research)
3. **Distillation** — extraction attacks do treningu konkurencyjnych modeli

Fable 5 ma **0% progress na offensive cyber tasks** w blocking mode (classifier skutecznie blokuje). ExploitBench 78.0% to wynik **Mythos 5**, nie Fable 5.

## Tier hierarchia Claude (po 9 czerwca 2026)

| Tier | Model | Cena ($/M in/out) | Status |
|------|-------|-------------------|--------|
| Mythos-class (restricted) | Claude Mythos 5 | $10/$50 | Tylko Project Glasswing |
| **Mythos-class (public)** | **Claude Fable 5** | **$10/$50** | **Nowy** |
| Flagship | Claude Opus 4.8 | $5/$25 | Poprzedni top tier |
| Mid | Claude Sonnet 4.6 | $3/$15 | Workhorse |
| Small | Claude Haiku 4.5 | $1/$5 | Szybki, tani |

Fable 5 kosztuje 2× więcej niż Opus 4.8. Różnica uzasadniona jest **premium benchmarkami**, nie raw capability. Dodatkowe koszty: prompt caching 90% rabatu, US-only inference 1.1× multiplier.

## Dostępność

| Kanał | Fable 5 | Mythos 5 |
|-------|---------|----------|
| Claude API | ✅ | ❌ |
| claude.ai Pro/Max/Team/Enterprise | ✅ (do 22.06 za darmo) | ❌ |
| Claude Code | ✅ | ❌ |
| AWS Bedrock | ✅ (`anthropic.claude-fable-5`, US East N. Virginia) | ❌ |
| Google Vertex AI | ✅ (`claude-fable-5`) | ❌ |
| Microsoft Foundry | ✅ | ❌ |
| **Project Glasswing** | — | ✅ |

## Polska i chińscy resellerzy (stan 9.06 wieczór)

| Provider | Fable 5 | Max model | ETA |
|----------|---------|-----------|-----|
| **VSLLM** | ❌ | (brak) | Wolny pipeline Anthropic |
| **aigcbest.top** (NewAPI/0api) | ❌ | Opus 4.7 | Piątek-niedziela (12-14.06) |
| **dmxapi.com** | ❌ | Opus 4.1 | 1-2 tygodnie |
| **siliconflow.cn** | ❌ | brak Claude | (tylko Qwen/DeepSeek/GLM/Kimi) |
| **nextai-code.com** | ❌ | Haiku 4-5 | — |
| **Wei-Shaw/claude-relay-service** | ❌ | Opus 4.7 | self-host, GitHub 12k⭐ |

Szacunek cen u resellerów (po adapt, marża 50-100%): aigcbest ~¥35-70/M input, ~¥175-350/M output. W USD: $5-10/M input, $25-70/M output (taniej niż Claude bezpośrednio dla płacących kartą zagraniczną).

## Open source vs closed

| Model | SWE-Bench Pro | Pricing ($/M in/out) | Tier |
|-------|---------------|----------------------|------|
| **Claude Fable 5** | **80.3%** | $10/$50 | Closed frontier |
| DeepSeek V4 Pro | 77.4% | $0.14/$0.28 | Open source |
| Claude Opus 4.8 | 69.2% | $5/$25 | Closed |
| GPT-5.5 | 58.6% | $5/$30 | Closed |
| Gemini 3.1 Pro | 54.2% | $1.25/$10 (preview) | Closed |

Wniosek: DeepSeek V4 daje 95% wartości Fable 5 za 1% ceny. Fable 5 ma sens tylko dla **specific high-leverage tasks**: long-horizon agentic coding, legacy migration 500K+ LOC, senior-level reasoning.

## Co obserwować

1. **Reakcja OpenAI** — GPT-5.6 w 1-2 tygodnie. Czy pójdą w dual-release?
2. **Google Gemini** — 3.1 Pro preview do GA czy czeka na 3.2?
3. **Meta** — Muse/Spark były setback, czy w ogóle wydadzą frontier?
4. **aigcbest** — ceny za 48-72h, marże prawdopodobnie 50-100%
5. **Anthropic IPO** — czerwiec 2026, Fable 5 to demo "responsible scaling"
6. **Biomedical trusted-access** — zapowiedziany program zwężenia bio/chem blokad

## Praktyczny plan dla programistów

**Dziś:** nic nie zmieniaj. Stack na Sonnet 4.6 / Opus 4.8 / DeepSeek V4 / Kimi K2.6.

**Za tydzień:** benchmark swojego najtrudniejszego real tasku na Fable 5 vs Opus 4.8. Zmierz: quality, latency, cost.

**Za miesiąc:** jeśli Fable 5 realnie bije Opus 4.8 na twoich taskach — przenieś **specific high-leverage flows** (legacy migration, complex refactor) na Fable 5. Reszta zostaje na tańszych.

**Za kwartał:** ceny u resellerów powinny spaść. Wtedy Fable 5 w $5-7/M input zaczyna mieć real ROI.

## Stripe Ruby Migration — case study

50M-line codebase zmigrowany w **1 dzień** vs **team of 2 months** robiący to samo ręcznie. To nie marketing — real customer data z Project Glasswing partnerów. Fable 5 iteruje po plikach, pisze patch, uruchamia testy i naprawia własny błąd. To jest real use case, nie demo.

## Źródła

1. Anthropic: https://www.anthropic.com/news/claude-fable-5-mythos-5
2. The Verge: https://www.theverge.com/news/946725/anthropic-releases-claude-fable-5-mythos
3. TechCrunch: https://techcrunch.com/2026/06/09/anthropic-released-claude-fable-5-its-most-powerful-model-publicly-days-after-warning-ai-is-getting-too-dangerous
4. CNBC: https://www.cnbc.com/2026/06/09/anthropic-mythos-claude-fable-5.html
5. SecurityWeek: https://www.securityweek.com/anthropic-launches-claude-fable-5-mythos-class-ai-with-cybersecurity-guardrails
6. VentureBeat: https://venturebeat.com/technology/anthropic-brings-mythos-to-the-masses-with-claude-fable-5-its-most-powerful-generally-available-model-ever
7. AWS blog: https://aws.amazon.com/blogs/aws/anthropic-claude-fable-5-on-aws-mythos-class-capabilities-with-built-in-safeguards-now-available
8. Anthropic docs: https://docs.anthropic.com/en/docs/about-claude/models
9. Reddit r/Anthropic: https://www.reddit.com/r/Anthropic/comments/1u1b1yj/introducing_claude_fable_5
10. Digital Applied: https://www.digitalapplied.com/blog/claude-fable-5-mythos-5-release-benchmarks-2026

---

*STEM News · auto-publikowane z wątku Discord 1512398228384120864 · GitHub Actions daily*
*Rozszerzane przez `MiniMax-M3` (vsllm) · Vanilla HTML+CSS · GitHub Pages*

![Claude Fable 5 - hero](../assets/img/fable5/01_hero_fable5.png)
![Before/After Fable 5](../assets/img/fable5/02_before_after.png)
![Claude tiers - Haiku/Sonnet/Fable](../assets/img/fable5/03_anthropic_tiers.png)
![Global AI compute race](../assets/img/fable5/04_ai_army.png)
![Solo developer vs hyperscalers](../assets/img/fable5/05_solo_developer.png)
![Open source AI treasure](../assets/img/fable5/06_open_source.png)