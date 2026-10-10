'use strict';

const crypto = require('node:crypto');
const { validateEvaluationCommand } = require('./contracts');
const { applyBasisPoints, parseMinorUnit, parseRateBps } = require('./money');
const { assessRule } = require('./rule-control');

function stable(value) {
  if (Array.isArray(value)) return value.map(stable);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.keys(value).sort().map((key) => [key, stable(value[key])]));
  }
  return value;
}

function hashInput(value) {
  return crypto.createHash('sha256').update(JSON.stringify(stable(value))).digest('hex');
}

function reviewRequired(command, reasons) {
  return {
    httpStatus: 200,
    body: {
      requestId: command && command.requestId,
      decision: 'REVIEW_REQUIRED',
      reasons,
      postingStatus: 'POSTING_BLOCKED'
    }
  };
}

function calculate(rule, facts) {
  const rateBps = parseRateBps(rule.parameters && rule.parameters.rateBps);
  if (rule.method === 'PERCENT_OF_BASE') {
    const baseMinor = parseMinorUnit(facts.baseAmountMinor, 'facts.baseAmountMinor');
    return {
      method: rule.method,
      baseAmountMinor: baseMinor.toString(),
      rateBps: Number(rateBps),
      taxAmountMinor: applyBasisPoints(baseMinor, rateBps).toString()
    };
  }
  if (rule.method === 'TEMPORARY_DIFFERENCE') {
    const carrying = parseMinorUnit(facts.carryingAmountMinor, 'facts.carryingAmountMinor');
    const taxBase = parseMinorUnit(facts.taxBaseAmountMinor, 'facts.taxBaseAmountMinor');
    const difference = carrying - taxBase;
    return {
      method: rule.method,
      carryingAmountMinor: carrying.toString(),
      taxBaseAmountMinor: taxBase.toString(),
      temporaryDifferenceMinor: difference.toString(),
      rateBps: Number(rateBps),
      taxAmountMinor: applyBasisPoints(difference, rateBps).toString()
    };
  }
  throw new TypeError('The governed rule calculation method is not supported.');
}

async function evaluateTax({ command, ruleRepository }) {
  const errors = validateEvaluationCommand(command);
  if (errors.length > 0) {
    return { httpStatus: 400, body: { error: 'INVALID_COMMAND', details: errors } };
  }

  const rule = await ruleRepository.findEffectiveRule({
    ruleId: command.ruleId,
    asOfDate: command.asOfDate
  });
  const reasons = assessRule(rule, command);
  if (reasons.length > 0) return reviewRequired(command, reasons);

  try {
    const calculation = calculate(rule, command.facts);
    const adjacency = command.taxType === 'PAYROLL_TAX'
      ? { primaryProcess: 'APQC 9.5.3', relationship: 'ADJACENT_PROCESS' }
      : command.taxType === 'CUSTOMS_EXCISE'
        ? { primaryProcess: 'APQC 9.11', relationship: 'ADJACENT_PROCESS' }
        : undefined;

    return {
      httpStatus: 200,
      body: {
        requestId: command.requestId,
        evaluationId: crypto.randomUUID(),
        decision: 'VALID',
        postingStatus: command.taxType === 'DEFERRED_TAX'
          ? 'IFRS_VALIDATION_REQUIRED'
          : 'TAX_DECISION_VALID',
        inputHash: hashInput(command),
        calculation,
        ruleEvidence: {
          ruleId: rule.ruleId,
          version: rule.version,
          effectiveFrom: rule.effectiveFrom,
          effectiveTo: rule.effectiveTo || null,
          authority: rule.authority,
          approval: rule.approval
        },
        processBoundary: adjacency
      }
    };
  } catch (error) {
    return {
      httpStatus: 400,
      body: { error: 'INVALID_FACTS_OR_RULE', message: error.message }
    };
  }
}

module.exports = { evaluateTax, hashInput };

