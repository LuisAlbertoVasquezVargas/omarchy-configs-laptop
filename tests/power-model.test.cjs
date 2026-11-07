// tests/power-model.test.cjs

const assert = require("node:assert/strict");
const { test } = require("node:test");
const model = require(process.env.POWER_MODEL_PATH);

const states = { Charging: 1, Discharging: 2, FullyCharged: 4, PendingCharge: 5 };

function battery(overrides = {}) {
  return {
    isPresent: true,
    percentage: 0.55,
    state: states.Charging,
    changeRate: 10,
    timeToFull: 3600,
    ...overrides,
  };
}

test("zero charging rate retains the charging icon", () => {
  const device = battery({ changeRate: 0, timeToFull: 0 });
  assert.equal(model.chargeThresholdActive(device, false, states), false);
  assert.equal(model.batteryIcon(device, false, states), model.batteryIcon(battery(), false, states));
});

test("low rate and long estimates do not imply a charge hold", () => {
  const device = battery({ changeRate: 0.1, timeToFull: 12 * 3600 });
  assert.equal(model.chargeThresholdActive(device, false, states), false);
  assert.equal(model.batteryIcon(device, false, states), model.batteryIcon(battery(), false, states));
});

test("pending charge on AC is a charge hold", () => {
  const device = battery({ state: states.PendingCharge });
  assert.equal(model.chargeThresholdActive(device, false, states), true);
  assert.equal(model.batteryIcon(device, false, states), model.batteryIcon(device, true, states));
});

test("fully charged below 99 percent is a charge hold", () => {
  assert.equal(model.chargeThresholdActive(battery({ state: states.FullyCharged, percentage: 0.8 }), false, states), true);
});

test("fully charged at 99 percent or above is not a charge hold", () => {
  for (const percentage of [0.99, 1]) {
    assert.equal(model.chargeThresholdActive(battery({ state: states.FullyCharged, percentage }), false, states), false);
  }
});

test("unplugging clears the charging icon even before the device state updates", () => {
  const device = battery({ changeRate: 0 });
  assert.equal(model.chargeThresholdActive(device, true, states), false);
  assert.equal(model.batteryIcon(device, true, states), model.batteryIcon(battery({ state: states.Discharging }), true, states));
  assert.notEqual(model.batteryIcon(device, true, states), model.batteryIcon(battery(), false, states));
});

test("discharging on AC does not imply a charge hold", () => {
  assert.equal(model.chargeThresholdActive(battery({ state: states.Discharging }), false, states), false);
});

test("a missing battery has no icon or charge hold", () => {
  assert.equal(model.chargeThresholdActive(null, false, states), false);
  assert.equal(model.batteryIcon(battery({ isPresent: false }), false, states), "");
});
