# UI/UX Guidelines

## Product Style

The interface must feel like a professional ToB operations system, not a
temporary crawler demo.

Design goals:

- clear hierarchy;
- low learning cost;
- restrained enterprise visual style;
- consistent interaction patterns;
- role-appropriate complexity.

## Global Layout

Use a consistent admin layout:

- left navigation;
- top status/user area;
- page title area;
- status summary area;
- toolbar;
- main content area;
- modal area.

## Menu Structure

Administrator:

- Overview
- Monitoring
- Run Center
- Report Center
- Resource Management
  - Platform Accounts
  - Proxy Resources
  - AI Access
- System Configuration
  - Users And Permissions
  - AI Evaluation Rules
  - Mail Configuration
  - Mail Templates
  - Runtime Strategy
  - System Diagnostics

Normal user:

- Overview
- Monitoring
- Run Center
- Report Center

## Page Structure

Every page should follow this structure:

1. Page title, short description, and primary action.
2. Status summary or key metrics.
3. Toolbar with search, filters, refresh, and batch actions when needed.
4. Main table/list/preview/log area.
5. Modal dialogs for add, edit, test, confirm, and login actions.

Avoid:

- one-off page layouts;
- large inline creation forms on first-level pages;
- repeated menus and tabs for the same function;
- showing administrator resource details to normal users.

## Modal Rules

Use modal dialogs consistently for:

- create;
- edit;
- test;
- login QR/status;
- delete confirmation;
- stop confirmation;
- resend confirmation.

Use large modal dialogs for:

- report preview;
- run logs;
- account login session details.

Do not mix drawer, inline form, and modal for the same operation category in
the first version.

## Normal User Task Wizard

Normal users create tasks through a simplified wizard:

1. Target
   - law firm name;
   - aliases.
2. Collection Content
   - platforms;
   - platform search terms;
   - crawl range;
   - comment collection.
3. Schedule
   - frequency;
   - send time when applicable.
4. Report
   - recipient emails.

Do not show these to normal users:

- account selection;
- proxy selection;
- AI profile selection;
- email template selection;
- browser mode;
- profile path;
- crawler command;
- debug status.

Administrators may access advanced options where needed.

## Administrator Resource Pages

Resource pages use:

- primary action button at top right;
- search and filters in the toolbar;
- table as the main content;
- create/edit in modal dialogs;
- status tags for resource state;
- clear error messages and latest check time.

Resource pages include:

- platform accounts;
- proxy resources;
- AI access;
- mail templates;
- users.

## Status Language

Normal-user language:

- Platform resource is available.
- Platform resource needs administrator attention.
- Task submitted.
- Report is generating.
- Report has been sent.

Administrator language:

- Account login state expired.
- Proxy connection failed.
- Account profile is currently in use.
- QR login timed out.
- Verification is required.

## Customer-Facing Forbidden Text

Do not show these in customer-facing UI:

- internal project names;
- command lines;
- local paths;
- profile paths;
- environment variable names;
- debug wording;
- demo wording;
- self-test wording;
- raw API keys, cookies, proxy passwords, or SMTP passwords.

## Interaction Feedback

Every action must provide feedback:

- loading state immediately after click;
- disabled button while executing;
- success toast;
- understandable error message;
- local refresh after success;
- confirmation for destructive actions.

Actions requiring feedback include:

- save task;
- run task;
- stop run;
- delete task;
- view logs;
- preview report;
- resend email;
- add account;
- start login;
- save proxy;
- test AI;
- test SMTP;
- save template;
- save runtime settings.

