# RevenueCat Shipaton 2026: The Big Picture & Winning Master Plan

> **Official Competition:** [RevenueCat Shipaton 2026: Ship apps and start making money](https://revenuecat-shipaton-2026.devpost.com/)  
> **Prize Pool:** ,000+ in cash (,000,000+ in total rewards, billboard spotlights, conferences, and prizes)  
> **Submission Window:** August 1, 2026 – September 30, 2026 (App Store / Google Play / Samsung Galaxy Store)

---

## 1. Executive Summary & Core Rules

The RevenueCat Shipaton is not a typical weekend hackathon. It is a **production-grade shipping sprint** aimed at launching live, monetizing mobile apps.

### Hard Eligibility Requirements
1. **Brand New Public Release:**
   - The app must be published for the first time on the **Apple App Store**, **Google Play Store**, or **Samsung Galaxy Store** between **August 1, 2026 and September 30, 2026**.
   - *Updates to previously released apps do not qualify.*
   - *Exception:* The **Next Gen Award** (student category, 13+) allows video + open-source repo submissions without requiring a paid store developer account.
2. **Mandatory RevenueCat Integration:**
   - Must use the **RevenueCat SDK** to power at least one in-app purchase (IAP) / subscription **OR** serve ads via **RevenueCat Ads**.
3. **Required Devpost Submission Deliverables:**
   - **Live Store URL:** Direct link to your published app on the App Store, Google Play, or Galaxy Store.
   - **Demo Video:** Maximum **2 minutes**, demonstrating the app running on an actual device (publicly hosted on YouTube or Vimeo, no copyrighted music/trademarks).
   - **Icon:** 1024 x 1024 px PNG/JPG.
   - **Screenshot:** At least one screenshot at **1179 x 2556 px** (without device frames or mockups).
   - **Access for Judges:** Free trial configured or working promo code to allow judges to unlock and test all premium features.
   - **Detailed Writeup:** Highlighting features, architecture, and eligibility for specific category tracks.

---

## 2. Competition Taxonomy & Prize Breakdown

`mermaid
mindmap
  root((Shipaton 2026))
    Main Awards
      Grand Prize 
      Build In Public  /  / 
      HAMM Monetization  /  / 
      RevenueCat Design  /  / 
      Catvertising Ads  /  / 
      Best Game  /  / 
      Peace Prize Social Good  /  / 
      Next Gen Student Track
    Influencer Tracks  each
      Productivity Christopher Lawley
      Nutrition Abbey's Kitchen
      Yoga & Fitness Simone Sharice
      Career Coaching Leadership Heather
      Gaming Backlog Mr Lewis
    Sponsor Tracks - each
      Ship Kotlin Everywhere JetBrains
      Best App for Galaxy Samsung
      Keep Them Coming Back OneSignal 
      Funnel Vision Stripe
      The Growth Loop Layers
      Most Viral App Noise
      Idea to Income Replit
`

### A. Core Flagship Awards
* **Grand Prize (,000 + Times Square Billboard + NYC Trip + 9to5Mac/Google Spotlight):** Awarded to the app demonstrating the most real-world user traction, revenue velocity, and growth momentum post-release.
* **#BuildInPublic (,000 1st / ,000 2nd / ,000 3rd):** Best documented build journey, transparent metrics, community engagement, and social media learnings.
* **HAMM Award (Help Apps Make Money) (,000 / ,000 / ,000):** Most innovative, robust monetization strategy (tiered paywalls, smart packages, dynamic offerings).
* **RevenueCat Design Award (,000 / ,000 / ,000):** Exemplary craft, seamless micro-interactions, delightful onboarding, and design elegance.
* **Catvertising Award (,000 / ,000 / ,000):** Creative, non-intrusive use of RevenueCat Ads alongside or blended with in-app purchases.
* **Best Game Award (,000 / ,000 / ,000):** Top mobile game with strong gameplay loop and genre-native monetization.
* **RevenueCat Peace Prize (,000 / ,000 / ,000):** Outstanding social impact and public good.

### B. Influencer Specification Tracks (,000 1st Place Each)
Each influencer brings an exact user problem and target demographic:
1. **Productivity (Christopher Lawley):** Fast, frictionless repository for Apple power users to capture, index, and retrieve reusable text snippets, docs, links, and media.
2. **Nutrition & Healthy Eating (Abbey's Kitchen):** Compassionate nutrition companion based on the Hunger Crushing Combo (protein, fiber, healthy fats) without restrictive calorie/macro counting.
3. **Yoga & Fitness (Simone Sharice):** Personalized movement and wellness companion answering *What should I do today?* (Pilates, mobility, recovery) without cognitive fatigue.
4. **Career Coaching (Leadership Heather):** Interactive workplace scenario simulator for first-time managers to practice tough conversations (giving feedback, setting boundaries, saying no).
5. **Gaming Backlog (Mr Lewis Blogs Gaming):** Backlog and bucket-list tracker making discovering, logging, and completing games enjoyable rather than a chore.

### C. Sponsor Technology Tracks (,000 - ,000 Each)
* **Ship Kotlin Everywhere (JetBrains - ):** High-polish app targeting iOS and Android using **Kotlin Multiplatform (KMP)** or Compose Multiplatform.
* **Best App for Galaxy (Samsung - ):** Published on the **Samsung Galaxy Store**, optimized for Samsung devices and foldables (Z Fold / Z Flip).
* **Keep Them Coming Back (OneSignal - ,000 1st / ,000 2nd / ,000 3rd):** Thoughtful retention architecture using OneSignal push notifications, automated user journeys, and segmented re-engagement.
* **Funnel Vision (Stripe - ):** High-converting web onboarding and checkout funnel powered by **RevenueCat Web Funnels + Stripe**.
* **The Growth Loop (Layers - ):** Scientific approach to growth using the **Layers SDK** to run and observe paywall A/B tests and conversion experiments.
* **Most Viral App (Noise - ):** Driving outsized awareness and install velocity through scalable, repeatable short-form video content formats (TikTok, Reels, Shorts).
* **Idea to Income (Replit - ):** Rapidly building, deploying, and monetizing from idea to live revenue using Replit.

---

## 3. The Prize-Stacking Matrix

Instead of scattering energy building disjointed prototypes, maximize winning probability through **Prize Stacking** - engineering an application that naturally qualifies for **5 to 7 categories simultaneously**.

`
+------------------------------------------------------------------------+
|                        User Acquisition Layer                          |
|  TikTok / Reels / Shorts (Noise Track) ---> Stripe Web Funnel (Stripe) |
+----------------------------------+-------------------------------------+
                                   | Deep Link / Sign In
+----------------------------------v-------------------------------------+
|                 Kotlin Multiplatform Core (JetBrains)                  |
|                                                                        |
|   +---------------------------+      +-------------------------------+ |
|   |     iOS / iPadOS / macOS  |      | Android + Galaxy Foldable Opt | |
|   |         (App Store)       |      |   (Play Store & Galaxy Store) | |
|   +-------------+-------------+      +---------------+---------------+ |
+-----------------+------------------------------------+-----------------+
                  |                                    |
+-----------------v------------------------------------v-----------------+
|                     RevenueCat & Retention Stack                       |
|  * RevenueCat Paywalls & Subscriptions (HAMM Award)                    |
|  * Layers SDK for Dynamic Paywall A/B Testing (Layers Track)           |
|  * OneSignal Push Notifications & User Journeys (OneSignal Track)      |
|  * RevenueCat Hybrid Ads fallback for free tier (Catvertising)         |
+------------------------------------------------------------------------+
`

### High-Yield Synergy Profiles

| Stacking Profile | Target Influencer Track | Sponsor Stack | Core Awards Targeted |
| :--- | :--- | :--- | :--- |
| **Profile A: The Enterprise Coach** | **Career Coaching** (Leadership Heather) | **JetBrains KMP** + **Samsung Galaxy Store** + **OneSignal** | **Grand Prize**, **HAMM Monetization**, **RevenueCat Design** |
| **Profile B: The Health & Wellness Funnel** | **Yoga & Fitness** (Simone Sharice) or **Nutrition** (Abbey's Kitchen) | **Stripe Web Funnel** + **Layers A/B Testing** + **OneSignal** | **Grand Prize**, **Most Viral (Noise)**, **HAMM Award** |
| **Profile C: The Power Productivity Hub** | **Productivity** (Christopher Lawley) | **RevenueCat Web Funnels** + **OneSignal** + **Galaxy Store** | **Design Award**, **HAMM Award**, **Grand Prize** |

---

## 4. End-to-End Execution Roadmap

### Phase 1: Foundations & Store Prerequisites (Week 1)
- [ ] **Developer Accounts:** Verify Apple Developer Program, Google Play Console, and Samsung Galaxy Store Developer accounts are active and identity-verified.
- [ ] **Track Selection:** Pick target Influencer brief + sponsor stack synergies.
- [ ] **RevenueCat Setup:** Create project in the RevenueCat dashboard; configure offerings, packages, entitlements, and webhooks.
- [ ] **Discord Community:** Join the Official Shipaton Discord and register on Devpost.

### Phase 2: MVP Sprint & SDK Integration (Weeks 2-4)
- [ ] **Feature Development:** Build core feature loop addressing the chosen influencer brief.
- [ ] **Paywall & Monetization:** Implement dynamic paywalls using Purchases SDK with monthly/annual tiers and a free trial.
- [ ] **Layers SDK:** Configure experiment variants to A/B test paywalls for the Layers Growth Loop Award.
- [ ] **OneSignal Messaging:** Set up automated welcome journeys, contextual activity reminders, and streak notifications.
- [ ] **Foldable & Tablet Optimization:** Implement multi-window and responsive layout handling for Samsung Galaxy devices.

### Phase 3: Web Funnel & App Store Submissions (Weeks 5-6)
- [ ] **Stripe Web Funnel:** Build an introductory onboarding quiz on the web that collects payment via Stripe/RevenueCat Web Funnels, delivering an activation link into the app.
- [ ] **Store Submissions (Buffer Alert):** Submit app builds to the App Store, Google Play, and Galaxy Store **no later than September 15-20** to allow for review cycles.
- [ ] **RevenueCat Ads Integration:** (Optional / Catvertising track) Enable ad banners/interstitials for free-tier users.

### Phase 4: Launch, Virality & Build-In-Public (Weeks 7-8)
- [ ] **Social Media Blitz:** Document technical breakthroughs, metrics, and design evolutions using #BuildInPublic and #Shipaton2026.
- [ ] **Noise Virality Push:** Post short-form videos demonstrating immediate value or before/after problem solving.
- [ ] **Devpost Assets:**
  - Record the 2-minute raw-device demo video.
  - Export the 1024 x 1024 app icon.
  - Capture clean 1179 x 2556 screenshots (no device bezels).
  - Generate judge promo codes / verify free trial.
- [ ] **Submit Devpost Entry:** Finalize all fields and submit prior to the September 30 deadline.

---

## 5. Submission Readiness Checklist

| Requirement | Specification | Status |
| :--- | :--- | :---: |
| **First Public Release** | Published between Aug 1 and Sep 30, 2026 | [ ] |
| **RevenueCat SDK** | Active IAP or RevenueCat Ads functioning in live binary | [ ] |
| **Demo Video** | <= 120 seconds, real device capture, YouTube/Vimeo public URL | [ ] |
| **App Icon** | Exactly 1024 x 1024 px PNG/JPG | [ ] |
| **Screenshots** | At least one raw 1179 x 2556 px screenshot without bezel frame | [ ] |
| **Judge Access** | Promo code or active free trial provided in submission form | [ ] |
| **Live Store Listing** | Direct App Store / Play Store / Galaxy Store URL | [ ] |
