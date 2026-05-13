# 🛠️ AI Agent for OSS Risk Mitigation – Workshop Day 2 Plan

_Goal: Move from idea → concrete architecture → MVP path that can be implemented in Jenkins._

---

## 1. Recap & Alignment (10–15 min)

### Objectives

- Ensure everyone understands yesterday’s problem slice, hypothesis, and target behavior.
    
- Confirm scope for the agent.
    

### Questions to ask the team

- _What is the most painful part today? Updating license info? Full analysis? Diff creation?_
    
- _What output is considered “good enough” for MVP?_
    
- _How automated should this be? Fully automatic or human-in-the-loop via PR review?_
    

---

## 2. Clarify the Agent’s Responsibilities (20 min)

Break down the steps the agent must perform.

### Suggested Categories

1. **Inputs needed**
    
    - Current firmware version
        
    - OSS component list (Yocto outputs, etc.)
        
    - Previous OSS RMP version
        
2. **Processing tasks**
    
    - Detect version changes
        
    - Run full vs. incremental analysis
        
    - Summarize component-level changes
        
    - Create or update OSS mitigation plan
        
    - Produce DIFF to previous version
        
3. **Outputs**
    
    - Updated OSS RMP file(s)
        
    - Markdown summary for Confluence
        
    - PR with changes in Git
        
    - Jenkins build result (pass/fail with feedback)
        

### DECISION POINT

➡️ **Define MVP scope:**  
Choose which 2–3 responsibilities will be implemented _first_.

---

## 3. Decide Where the Agent Runs (20–30 min)

Present the options and evaluate together.

### Option A – Inside existing Jenkins pipeline

- Simple to integrate
    
- Easy to trigger on build or release
    
- Well-known environment
    

### Option B – External orchestrator (n8n, Temporal) – _not in scope for sprint_

- Future interest
    

### DECISION POINT

➡️ **Pick the execution environment for MVP**  
(Almost always Jenkins for simplicity)

---

## 4. Strategy for Remembering “Previous State” (20–25 min)

### Options

1. **Store results in Git (recommended)**
    
    - Agent commits analysis results (JSON/YAML/Markdown)
        
    - Opens a PR when changes occur
        
    - Reviewable, auditable
        
2. **Store results in Confluence**
    
    - Easy for humans, harder for diff & automation
        
3. **Store results in S3 bucket or artifact repository**
    
    - Clean storage, but harder for collaboration
        

### DECISION POINT

➡️ **Where does the “truth” of OSS analysis live?**  
Most teams select **Git repository**.

---

## 5. Define Version Change Logic (15–20 min)

### Key questions to the customer

- _How do we detect a what type of case case?_
    
- _Where does version metadata come from?_
    
- _Should we compare component versions or entire firmware manifest?_
    

### Define behavior

|Scenario|Action|
|---|---|
|Firmware version changed|Run full analysis|
|Same version, minor component updates|Run incremental analysis|
|No changes|Skip analysis, report "no changes"|

### DECISION POINT

➡️ **Agree on the rules for triggering full vs. incremental analysis.**

---

## 6. Define Diffs & Reporting (20 min)

Ask the team:

- _What exactly is the diff report expected to contain?_
    
- _Is diff calculated per component, per license, per risk score?_
    
- _What should a “changed component” look like in the report?_
    

Define MVP output format, e.g.:

```
## OSS RMP Diff (v1.2 → v1.3)

### New Components
- libfoo 1.0 → 1.2 (GPLv2)

### Removed Components
- bar-utils (MIT)

### Changed Risk Assessment
- openssl: Risk High → Medium (reason: upstream fix)
```

---

## 7. Design the Jenkins Workflow (25–35 min)

Draw a plan (Paper/PP/Miro)

### Proposed minimal workflow

1. **Trigger**
    
    - Release build completed OR
        
    - Jenkins job triggered manually
        
2. **Steps**
    
    - Checkout firmware repo
        
    - Extract OSS component list (Yocto, SBOM, etc.)
        
    - Retrieve previous analysis from Git
        
    - Determine full vs. incremental analysis
        
    - Call AI Agent to:
        
        - Compare
            
        - Generate updated OSS RMP plan
            
        - Produce diff summary
            
    - Commit results to a PR
        
3. **Outputs**
    
    - PR in Git with updated analysis
        
    - Diff report attached to build artifacts
        
    - Build status (success/failure)
        

### DECISION POINT

➡️ **Agree on the exact Jenkins stages and success criteria.**

---

## 8. Define AI Agent Architecture (30 min)

Breakdown:

### Skills the agent needs

- Understand SBOM / OSS component metadata
    
- Recognize version changes
    
- Apply risk mitigation heuristics
    
- Generate structured documentation (RMP)
    
- Produce high-level human-readable summaries
    

### Inputs to Agent

- SBOM or license file(s)
    
- Previous RMP JSON / MD
    
- Component metadata
    
- Version info
    

### Outputs from Agent

- Updated RMP (JSON/MD)
    
- Diff
    
- Summary for PR description
    

### DECISION POINT

➡️ **Agree on the RMP data model** (JSON/Markdown?)  
➡️ **Agree on agent input & output schema**.

---

## 9. Outline the Technical PoC Plan (15–20 min)

Create a mindset: _What can we demo in with ~6 hour of work?_

### PoC Steps

1. Hardcode small SBOM example
    
2. Implement simple diff logic
    
3. Use LLM (Anthropic API key) to:
    
    - Update component descriptions
        
    - Generate mitigation plan text
        
4. Push output to Git
    
5. Create PR
    

### Deliverables for demo

- Example PR with updated RMP
    
- Jenkins build showing agent logs
    
- Before / After diff visualized
    

---

## 10. Final Decision Summary (10 min)

Write down:

- Where the agent runs --> For demo it is viable to run locally
    
- How previous state is stored
    
- Minimum viable features
    
- Success metrics for next sprint
    
- Owners for each part
    

---

# Helper Questions

### Understanding needs

- _What information must always be included in OSS RMP?_
    
- _What parts must humans still review?_
    
- _What is highest cost today: searching, updating, or documenting?_
    

### Technical decisions

- _How do we extract the SBOM?_
    
- _Where does version number live?_
    
- _Do we need per-component "analysis fingerprint"?_
    

### Governance (IMO: Out of Scope )

- _Who approves the PR?_
    
- _Should agent runs be logged for audits?_
    
- _What happens if analysis fails?_
    

