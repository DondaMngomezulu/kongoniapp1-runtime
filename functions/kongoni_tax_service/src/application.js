'use strict';

const { evaluateTax } = require('./evaluate-tax');
const { validatePosting } = require('./validate-posting');

const CAPABILITIES = Object.freeze({
  serviceId: 'KNG-SVC-TAX-001',
  serviceName: 'Kongoni Tax Microservice',
  version: '0.1.0',
  status: 'DEVELOPMENT_CANDIDATE',
  apqcScope: {
    parent: '9.9',
    activities: [
      '9.9.1.1', '9.9.1.2', '9.9.1.3', '9.9.2.1', '9.9.2.2',
      '9.9.2.3', '9.9.2.4', '9.9.2.5', '9.9.2.6', '9.9.2.7'
    ]
  },
  calculationMethods: ['PERCENT_OF_BASE', 'TEMPORARY_DIFFERENCE'],
  taxTypes: [
    'VAT', 'CORPORATE_INCOME_TAX', 'CAPITAL_GAINS_TAX', 'DEFERRED_TAX',
    'WITHHOLDING_TAX', 'PAYROLL_TAX', 'CUSTOMS_EXCISE', 'OTHER'
  ],
  controls: [
    'NO_EMBEDDED_TAX_RATES',
    'APPROVED_EFFECTIVE_RULE_REQUIRED',
    'AUTHORITY_AND_CLAUSE_TRACEABILITY_REQUIRED',
    'JOINT_SARS_IFRS_GATE_FOR_DEFERRED_TAX_POSTING',
    'FAIL_CLOSED'
  ]
});

function result(statusCode, body) {
  return { statusCode, body };
}

function createApplication({ ruleRepository, clock = () => new Date() }) {
  if (!ruleRepository || typeof ruleRepository.findEffectiveRule !== 'function') {
    throw new TypeError('A rule repository is required.');
  }

  return {
    async handle(request) {
      const method = String(request.method || '').toUpperCase();
      const path = request.path || '/';

      if (method === 'GET' && path === '/health') {
        return result(200, {
          status: 'UP',
          serviceId: CAPABILITIES.serviceId,
          version: CAPABILITIES.version,
          ruleMode: ruleRepository.mode || 'UNKNOWN',
          timestamp: clock().toISOString()
        });
      }

      if (method === 'GET' && path === '/v1/capabilities') {
        return result(200, CAPABILITIES);
      }

      if (method === 'POST' && path === '/v1/evaluations') {
        const outcome = await evaluateTax({
          command: request.body,
          ruleRepository
        });
        return result(outcome.httpStatus, outcome.body);
      }

      if (method === 'POST' && path === '/v1/posting-validations') {
        const outcome = validatePosting(request.body);
        return result(outcome.httpStatus, outcome.body);
      }

      return result(404, {
        error: 'ROUTE_NOT_FOUND',
        message: 'The requested route does not exist.'
      });
    }
  };
}

module.exports = { CAPABILITIES, createApplication };

