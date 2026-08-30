'use strict';

function parseMinorUnit(value, fieldName) {
  if (typeof value !== 'string' || !/^-?\d+$/.test(value)) {
    throw new TypeError(`${fieldName} must be an integer string in minor units.`);
  }
  return BigInt(value);
}

function parseRateBps(value) {
  if (!Number.isSafeInteger(value) || value < 0 || value > 1000000) {
    throw new TypeError('The governed rule rateBps must be an integer from 0 to 1000000.');
  }
  return BigInt(value);
}

function divideRoundHalfAwayFromZero(numerator, denominator) {
  const negative = numerator < 0n;
  const absolute = negative ? -numerator : numerator;
  const quotient = absolute / denominator;
  const remainder = absolute % denominator;
  const rounded = remainder * 2n >= denominator ? quotient + 1n : quotient;
  return negative ? -rounded : rounded;
}

function applyBasisPoints(baseMinor, rateBps) {
  return divideRoundHalfAwayFromZero(baseMinor * rateBps, 10000n);
}

module.exports = { applyBasisPoints, parseMinorUnit, parseRateBps };

