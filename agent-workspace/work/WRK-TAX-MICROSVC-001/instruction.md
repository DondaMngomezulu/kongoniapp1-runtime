# Instruction — WRK-TAX-MICROSVC-001

Develop a governed tax microservice for APQC 9.9. Add a trigger for ChatGPT and a trigger for Catalyst Signals. Publish the verified source to `feat/kng-svc-tax-001` and open one draft pull request.

The implementation must meet these controls:

- It must not embed a production tax rate.
- It must use only approved and effective-dated executable rules.
- It must fail closed when a rule, authority, approval, input, or environment control is incomplete.
- It must keep Production outside the authorized scope.
- It must not replace a requested event with a polling schedule.
- It must record source publication separately from live Catalyst provisioning.
