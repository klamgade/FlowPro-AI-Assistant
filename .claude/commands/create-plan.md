# Create Implementation Plan

Create a detailed implementation plan for the requested feature or workflow.

This workspace is currently focused on developing the **MedChemExpress (MCE) CRM-Lite automation system**, which aims to consolidate sales reports, enquiry reports, and client activities into a structured master client dataset.

---

## Your Task

When the user runs this command, you must:

1. Understand the requested feature or workflow.
2. Analyse the existing project context and the requirement files related to MCE requirement and workflow automation.
3. Produce a **clear implementation plan** that developers can execute.
4. Save the output under:

plans/YYYY-MM-DD-{descriptive-name}.md

---


## Project Context

The current project is **MCE CRM-Lite Automation**.

The goal is to build a lightweight CRM-style system that:

- Consolidates **all clients and prospects into a Master Client File**
- Links **sales orders and enquiry reports to the correct client**
- Tracks **client engagement and activity history**
- Enables **basic reporting and insights**
- Reduces manual effort when new reports arrive

The system should remain **simple, lightweight, and automation-driven**, not a full CRM.

---

## Typical System Flow

Most features should fit into this structure:

Report Upload  
→ Data Parsing  
→ Client Matching  
→ Master Client Record Update  
→ Activity Logging  
→ Reporting or Insights

Automation tools such as **n8n, Make.com, or simple scripts** may be used.

---

## Plan Requirements

The plan must include:

### 1. Overview
Explain what the change or feature accomplishes.

### 2. Current State
Describe how the process currently works and what problem exists.

### 3. Proposed Changes
Explain what will be built and how it improves the system.

### 4. Architecture / Workflow
Describe the workflow or system components.

Example structure:

Upload Report  
→ Parse Data  
→ Match Client  
→ Update Master Client Table  
→ Log Activity

### 5. Files or Components Required

Examples:

- Data tables
- automation workflows
- parsing scripts
- database schema
- integrations

### 6. Step-by-Step Implementation Tasks

Provide clear steps developers can follow.

### 7. Validation Criteria

Define how to confirm the feature works correctly.

Example:

- Uploading a report automatically updates client records
- Duplicate clients are not created
- Activity history is logged

---

## Design Principles

Follow these rules when planning:

- Start with **simple, testable MVP workflows**
- Prefer **automation over heavy software builds**
- Ensure the system produces **a single source of truth for clients**
- Avoid building unnecessary complexity

---

## Output Format

Produce the final document using the standard plan format used in this workspace and save it under:

plans/YYYY-MM-DD-{descriptive-name}.md