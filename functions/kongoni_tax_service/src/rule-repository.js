'use strict';

class UnconfiguredRuleRepository {
  constructor() {
    this.mode = 'FAIL_CLOSED_UNCONFIGURED';
  }

  async findEffectiveRule() {
    return null;
  }
}

class InMemoryRuleRepository {
  constructor(rules = []) {
    this.mode = 'TEST_ONLY_IN_MEMORY';
    this.rules = rules;
  }

  async findEffectiveRule({ ruleId }) {
    return this.rules.find((rule) => rule.ruleId === ruleId) || null;
  }
}

module.exports = { InMemoryRuleRepository, UnconfiguredRuleRepository };

