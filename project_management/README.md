# Project Management Documentation

This folder contains project management artifacts to track progress, tasks, and technical decisions across working sessions.

## Files

### 📋 [TASKS.md](TASKS.md)
**Purpose:** Track all project tasks organized by status and priority

**When to use:**
- Start of each session: Review "In Progress" and "To Do" sections
- During work: Move tasks between sections as you complete them
- End of session: Update with any new tasks discovered

**Sections:**
- 🟢 Completed - Done and verified
- 🟡 In Progress - Currently working on
- 🔴 To Do - Organized by priority (High/Medium/Low)
- 📋 Backlog - Future work, not yet prioritized

### 📊 [STATUS.md](STATUS.md)
**Purpose:** Snapshot of current project state

**When to use:**
- Start of session: Quick context refresh
- After major changes: Update to reflect new state
- When onboarding: Understand what's working and what's not

**Contents:**
- Overview of transformation completion
- Current package structure
- Test status
- Known issues
- Next session priorities

### 🎯 [NEXT_STEPS.md](NEXT_STEPS.md)
**Purpose:** Concrete actions for the next working session

**When to use:**
- **START HERE** at beginning of each session
- End of session: Update with what should happen next
- When stuck: Refer to immediate actions

**Format:**
- Immediate actions with time estimates
- Step-by-step guides for complex tasks
- Decision points requiring input
- Future session plans

### 🔧 [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md)
**Purpose:** Track known issues, shortcuts, and improvements needed

**When to use:**
- When you notice something that should be fixed later
- Planning refactoring sessions
- Prioritizing cleanup work
- Understanding why code is "weird"

**Structure:**
- Organized by priority (High/Medium/Low)
- Each item has: Issue, Location, Impact, Effort, Risk
- Architecture debt from sprint plans
- Decision log for historical context

## Workflow

### Starting a New Session

1. **Read [NEXT_STEPS.md](NEXT_STEPS.md)** - Get immediate context (5 min)
2. **Scan [TASKS.md](TASKS.md)** - See what's in progress (2 min)
3. **Check [STATUS.md](STATUS.md)** - Understand current state (3 min)
4. **Begin work** - Pick a task and mark it "In Progress"

### During Work

- Update [TASKS.md](TASKS.md) as you complete items
- Add new issues to [TECHNICAL_DEBT.md](TECHNICAL_DEBT.md) when discovered
- Make notes in [NEXT_STEPS.md](NEXT_STEPS.md) about blockers or decisions

### Ending a Session

1. **Mark completed tasks** in [TASKS.md](TASKS.md)
2. **Update [STATUS.md](STATUS.md)** with current state
3. **Write [NEXT_STEPS.md](NEXT_STEPS.md)** for next session
4. **Add any new technical debt** discovered

## Quick Reference

**Current Project State:**
- ✅ Package renamed to `healthcare_news_scraper`
- ✅ Documentation updated
- ⚠️ Internal naming still uses "Event" terminology
- ❓ Tests not verified since transformation

**Next Priority:**
- Run test suite to verify everything works
- Decide on internal naming strategy
- Address high-priority technical debt

## Tips

- **Be specific in NEXT_STEPS.md**: Include file paths, command examples, time estimates
- **Keep TASKS.md updated**: Don't let completed items sit in "In Progress"
- **Track decisions**: Use TECHNICAL_DEBT.md decision log for architectural choices
- **Use time estimates**: Helps with session planning and prevents scope creep

## Integration with Other Docs

- **Sprint Plans** (`sprints/`): Historical TDD planning, keep for reference but not active tracking
- **CHANGELOG.md**: User-facing changes, update when releasing versions
- **README.md**: Public documentation, keep high-level
- **This folder**: Internal project management, be detailed and specific
