# AI Persona Evaluation Report
**Candidate:** Sanskar Dubey | **Role:** AI Engineer Intern (SCALER)

## 1. Voice Quality & Metrics
I utilized the **Vapi.ai Analysis Dashboard** to natively measure latency across my test calls.
* **First-Response Latency:** Sub-1000ms. I configured the agent to speak first (`"Assistant speaks first"`) upon call connection, resulting in a near-instant zero-latency greeting. 
* **Average Turn Latency (Real-time measured):** `~750ms` (after optimization; initial baseline was `2506ms`)
  * *Transcriber (Deepgram flux):* `100ms` avg
  * *LLM (Groq llama-3.1-8b-instant):* `300ms` avg
  * *Voice/TTS (Deepgram Asteria):* `250ms` avg
  * *Endpointing:* `100ms` avg
* **Latency Optimization Journey:** Initial stack used Gemini 2.5 Flash (1028ms) + 11labs (424ms) = ~2500ms avg. By switching the voice agent's LLM to Groq's LPU-accelerated inference and TTS to Deepgram Aura, I achieved a **70% latency reduction** to ~750ms while maintaining tool-calling accuracy.
* **Transcription Accuracy:** Exceptionally high; Deepgram accurately handled both standard English and Indian accents without degrading conversational flow.
* **Task Completion Rate:** Tested across 10 independent calls focusing on the booking flow. The agent achieved a **100% Task Completion Rate** (10/10) for autonomously checking calendar availability and serving the Cal.com booking link when requested.

## 2. Chat Groundedness & Retrieval
I evaluated hallucination and groundedness using a **Manual Labeling** approach against an adversarial "Golden Q&A" set.
* **Hallucination Rate:** **0%** across 15 adversarial tests.
* **Measurement Methodology:** I subjected the chat interface to a rigorous test suite including: prompt injections (DAN prompts), out-of-bounds technical questions ("Explain K8s deployment"), and fake-resume traps ("Tell me about your MIT PhD").
* **Retrieval Quality (Precision/Recall):** The RAG pipeline (ChromaDB + Gemini Embeddings) achieved near 100% recall over my specific 7-project corpus. Precision was tightly controlled by strict System Prompts instructing the model to reply *"I don't have that specific detail mapped in my memory"* if context was missing.

## 3. Failure Modes Discovered & Fixed
1. **Failure Mode:** Intermittent 503 "Service Unavailable" errors crashing the backend.
   * **Root Cause:** Gemini 2.5 Flash API experiencing high demand/rate-limit spikes.
   * **The Fix:** Implemented a resilient Python wrapper with **Exponential Backoff Retry** logic (3s, 6s, 9s), allowing the backend to invisibly survive API spikes and eventually return a `200 OK` without the user noticing.
2. **Failure Mode:** Model hallucinating literal text `Tool Call: check_calendar()` instead of executing it.
   * **Root Cause:** Initial `/chat` endpoint was standard text-in/text-out without native function calling enabled.
   * **The Fix:** Completely rewrote the FastAPI endpoint to utilize **Gemini Native Function Calling** with a bounded 5-round execution loop.
3. **Failure Mode:** Twilio trial number rejecting incoming calls from unverified evaluators.
   * **Root Cause:** Twilio's strict Trial Account regulations restrict inbound/outbound calls to pre-verified numbers only.
   * **The Fix:** Bypassed Twilio trial restrictions by provisioning the phone number directly through Vapi's SIP trunking using introductory credits, ensuring the number is globally accessible.

## 4. Architectural Tradeoff
**Tradeoff Made:** *Dual-LLM Strategy — Voice Latency vs. Chat Accuracy*
I consciously chose to use **different LLMs for voice and chat**. The voice agent uses **Groq (Llama 3.1 8B Instant)** for sub-300ms inference latency, critical for natural conversation flow. The chat interface uses **Gemini 2.5 Flash** for its superior function-calling accuracy and deep reasoning over RAG context.
* **Why not one model for both?** GPT-4o would unify the stack but at ~2x cost and ~3x latency for voice. A single Groq model for chat would sacrifice RAG grounding quality. The dual-LLM approach gives us the best of both worlds: **750ms voice latency** with **0% chat hallucination rate**, at a combined cost of only ~$0.07/min (voice) and <$0.001/session (chat).

## 5. What I’d Build With 2 More Weeks
1. **Semantic Caching:** Implement Redis-based semantic caching (e.g., using GPTCache) so repeated questions (like "Tell me about yourself") bypass the LLM entirely, dropping latency to <100ms.
2. **Agentic Workflows:** Upgrade the linear function-calling loop to a full **LangGraph** deterministic state machine, allowing the agent to handle complex, multi-turn interview negotiations (e.g., rescheduling, calendar conflict resolution).
3. **Automated Evals Framework:** Move from manual labeling to an automated LLM-as-a-Judge pipeline (using Ragas or TruLens) integrated directly into a CI/CD pipeline for regression testing.
