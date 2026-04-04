/**
 * Hacker Configuration Schema
 *
 * Project-level configuration for the Hacker evolution engine.
 * Drop a `hacker.config.ts` (or .yaml/.json) in your project root.
 *
 * The core loop is fixed (run → score → diagnose → explore → select → mutate → rerun → decide).
 * Everything below configures the *policy* within that loop.
 *
 * Dependency: candidates are `.agent.md` files managed by [subagent-harness](https://www.npmjs.com/package/subagent-harness).
 * Install: `pnpm install` / `npm install` in this repo root, then import from this file or from `subagent-harness` directly.
 */

import type { PatchOp, RuntimeTarget } from "subagent-harness";

// ---------------------------------------------------------------------------
// Re-exported harness types + APIs (single source of truth = npm package)
// ---------------------------------------------------------------------------

export type {
  ExtensionValidator,
  RichAgentDocument,
  RichAgentFrontmatter,
  PatchOp,
  RuntimeTarget,
  ValidateOptions,
  ValidationIssue,
  ValidationResult,
} from "subagent-harness";

export {
  composeSubagent,
  parseRichAgentMarkdown,
  patchAgent,
  serializeAgent,
  serializeExtensions,
  SUPPORTED_SCHEMA_VERSIONS,
  validateRichAgent,
} from "subagent-harness";

// ---------------------------------------------------------------------------
// Top-level config
// ---------------------------------------------------------------------------

export interface HackerConfig {
  candidate: CandidateConfig;
  evaluation: EvaluationConfig;
  explore: ExploreConfig;
  mutation: MutationConfig;
  acceptance: AcceptanceConfig;
  stages?: StageConfig[];
  guards: GuardConfig;
}

// ---------------------------------------------------------------------------
// Candidate — the `.agent.md` being optimized
// ---------------------------------------------------------------------------

export interface CandidateConfig {
  path: string;           // relative path to the `.agent.md` source file
  target: RuntimeTarget;  // compose target for worker dispatch
  profile?: string;       // optional Harness profile to activate during compose
}

// ---------------------------------------------------------------------------
// Evaluation — how outputs are scored
// ---------------------------------------------------------------------------

export interface ScoringDimension {
  name: string;
  weight: number; // 0–1, weights should sum to 1
  floor?: number; // per-dimension minimum; fail if any case scores below
}

export interface EvaluationConfig {
  dimensions: ScoringDimension[];
  hardChecks?: string[]; // binary pass/fail (e.g. "format_valid", "safety_pass")
  stabilityWindow?: number; // consecutive epochs within ±threshold to consider stable
  stabilityThreshold?: number; // default 0.5
}

// ---------------------------------------------------------------------------
// Explore — evidence sourcing before mutation
// ---------------------------------------------------------------------------

export type ExploreProviderType =
  | "web_search"
  | "skill_hub"
  | "local_memory"
  | "custom";

export interface ExploreProvider {
  type: ExploreProviderType;
  name: string; // e.g. "google", "clawhub", "lobehub", "cursor-skills"
  endpoint?: string; // API endpoint if applicable
  apiKey?: string; // resolved at runtime, not stored in config
}

export interface ExploreBudget {
  maxProviderCalls: number; // total API calls across all providers per cycle
  maxEvidenceCards: number; // top-K evidence to carry into Select
  timeoutMs?: number;
}

export interface ExploreConfig {
  enabled: boolean;
  providers: ExploreProvider[];
  budget: ExploreBudget;
}

// ---------------------------------------------------------------------------
// Evidence Card — structured output from Explore
// ---------------------------------------------------------------------------

export interface EvidenceCard {
  id: string;
  sourceRef: string; // URL or internal reference (traceable)
  artifactType: "skill" | "prompt" | "pattern" | "paper" | "discussion";
  artifact: string; // normalized snippet or pointer
  hypothesis: string; // which failure mode it addresses
  risk: string; // potential side effects
  confidence: number; // 0–1 estimated relevance
}

// ---------------------------------------------------------------------------
// Mutation — how candidates are changed
// ---------------------------------------------------------------------------

export interface MutationOperator {
  id: string; // e.g. "add_constraint", "remove_constraint", "rephrase"
  description: string;
  appliesWhen: string; // human-readable trigger condition
  targetPath?: string; // default PatchOp.path this operator typically uses (e.g. "body")
}

export interface MutationConfig {
  operators: MutationOperator[];
  requireEvidenceLink: boolean; // mutation must reference ≥1 EvidenceCard
  maxMutationsPerCycle: 1; // hard invariant — always 1
}

// The actual mutation applied in a cycle. Links operator → evidence → patch.
export interface AppliedMutation {
  operatorId: string;
  evidenceCardIds: string[]; // which Evidence Cards supported this mutation
  patch: PatchOp;            // the single patchAgent() operation applied
  hypothesis: string;        // why this change should improve the diagnosed failure
}

// ---------------------------------------------------------------------------
// Acceptance — when to accept or rollback
// ---------------------------------------------------------------------------

export interface AcceptanceConfig {
  minOverallImprovement: number; // e.g. 0.1
  maxSingleCaseDrop: number; // e.g. 1.5 — rollback if any case drops more
  requireAllHardChecks: boolean;
  requireDimensionFloors: boolean; // enforce per-dimension floors from EvaluationConfig
}

// ---------------------------------------------------------------------------
// Stages — optional phased curriculum
// ---------------------------------------------------------------------------

export interface StageGate {
  dimension: string;
  operator: ">=" | "<=" | "==" | "none_below";
  value: number;
}

export interface StageConfig {
  name: string;
  focus: string; // human-readable goal
  gates: StageGate[];
  advanceWhen: "stable"; // requires stabilityWindow consecutive stable epochs
}

// ---------------------------------------------------------------------------
// Guards — global invariants
// ---------------------------------------------------------------------------

export interface GuardConfig {
  maxMutationsPerCycle: 1; // enforced at runtime, not configurable
  fullCorpusRerun: true; // enforced at runtime, not configurable
  workerIsolation: true; // enforced at runtime, not configurable
  maxCyclesBeforeStop?: number; // circuit breaker
  maxCyclesWithoutImprovement?: number; // early stopping
}

// ---------------------------------------------------------------------------
// Cycle Record — the structured output of Step 10 (Log)
// ---------------------------------------------------------------------------

export interface CycleRecord {
  cycle: number;
  candidateVersion: string; // git SHA or version tag of the .agent.md
  diagnosis: {
    worstCase: string;    // test case ID
    failureMode: string;  // human-readable description
    hypothesis: string;   // testable prediction
  };
  evidenceUsed: EvidenceCard[];
  mutation: AppliedMutation;
  beforeScores: Record<string, number>; // per-case or per-dimension
  afterScores: Record<string, number>;
  decision: "accept" | "rollback";
  lesson: string; // what was learned regardless of accept/rollback
}
