# Legal Sentiment Monitor Goal

## Product Definition

Legal Sentiment Monitor is a server-deployed ToB public-opinion monitoring
system for law-firm related social-media content.

The system lets normal users create monitoring tasks from a web UI. The system
then uses administrator-maintained platform accounts, proxies, AI access, email
settings, and runtime policies to complete collection, evaluation, reporting,
and email delivery.

## First-Version Goal

The first version must support a single-server, low-concurrency deployment:

- users access the system through a browser and domain name;
- administrators maintain platform accounts, proxies, AI access, mail settings,
  templates, users, and runtime strategy;
- normal users create monitoring tasks by choosing platforms, entering platform
  search terms, setting frequency, and entering recipient emails;
- platform login is completed through the web UI with server-side browser
  sessions and QR/status feedback;
- the system persists account profiles on the server and reuses them for later
  tasks;
- AI evaluation is optional; if AI is missing or fails, content enters manual
  review;
- email delivery is optional; reports can still be generated without email;
- reports use "suspected negative leads" wording and avoid factual conclusions.

## Roles

### System Administrator

The administrator owns resource supply and system maintenance:

- manage users and roles;
- manage platform account pool;
- manage proxy IP pool;
- manage AI access profiles;
- manage AI evaluation rules;
- manage SMTP and email templates;
- manage runtime strategy and system diagnostics;
- view all tasks, runs, logs, reports, and resource errors.

### Normal User

The normal user submits monitoring needs:

- create monitoring tasks;
- choose platforms;
- enter platform search terms;
- configure crawl frequency;
- enter report recipient emails;
- view own runs and reports.

Normal users must not need to understand account pools, proxies, browser
profiles, local paths, API keys, SMTP passwords, or crawler commands.

### Reserved Roles

These roles are reserved for later versions:

- reviewer;
- read-only viewer;
- workspace administrator;
- platform super administrator.

## First-Version Boundaries

V1 includes:

- user login and basic role permissions;
- administrator resource center;
- simplified normal-user task wizard;
- server-side QR login flow;
- account profile persistence;
- account/profile/proxy locking;
- runtime settings page;
- run center;
- report center;
- AI evaluation fallback;
- email report generation;
- server-like container or server validation.

V1 does not include:

- captcha bypass;
- SMS receiving automation;
- complex account rotation;
- dynamic proxy switching;
- high-concurrency worker cluster;
- public SaaS billing;
- open self-registration;
- field-level authorization;
- anti-verification promises.

## Server Acceptance Boundary

Local Chrome success is not production acceptance.

Production-like acceptance must prove that:

- the system runs in a server-like environment;
- the browser used for login and crawling runs on the server/container;
- QR codes or login states are returned to the web UI;
- profiles persist after browser close and service/container restart;
- tasks can run without requiring the operator's local Chrome.

## Key Acceptance Criteria

- Administrator can maintain platform accounts and proxies.
- Normal user can create a monitoring task without touching account or proxy
  settings.
- A task can run with selected platforms and platform search terms.
- The system can use a server-side account profile for crawling.
- Multiple accounts on the same platform do not share profiles.
- The same account/profile cannot be used concurrently.
- Proxy priority is task proxy, account proxy, then default network.
- AI failure does not block collection or report generation.
- Email failure does not block collection or report generation.
- Sensitive values are encrypted or masked.
- Runtime settings can be managed without code changes.

