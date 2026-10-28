const assert = require('node:assert/strict')
const { test } = require('node:test')
const Model = require('./Model.js')

const states = { Charging: 1, Discharging: 2, FullyCharged: 4, PendingCharge: 5 }
const battery = { isPresent: true, percentage: 0.6, state: states.Charging }

test('plug-in keeps the charging icon while UPower rate estimates catch up', () => {
  // Observed transition: Charging with zero rate for 10 seconds, then 5.427 W.
  for (const changeRate of [0, 5.427]) {
    const device = { ...battery, changeRate, timeToFull: 0 }
    assert.equal(Model.chargeThresholdActive(device, false, states), false)
    assert.equal(Model.modeLabel(device, false, states), 'Charging')
    assert.equal(Model.batteryIcon(device, false, states), '󰢞')
  }
})

test('a long charging estimate does not hide the charging icon', () => {
  const device = { ...battery, changeRate: 2.373, timeToFull: 37274 }
  assert.equal(Model.modeLabel(device, false, states), 'Charging')
  assert.equal(Model.batteryIcon(device, false, states), '󰢞')
})

test('explicit charge holds retain their threshold label and normal icon', () => {
  for (const state of [states.PendingCharge, states.FullyCharged]) {
    const device = { ...battery, state }
    assert.equal(Model.modeLabel(device, false, states), 'Threshold')
    assert.equal(Model.batteryIcon(device, false, states), '󰂀')
    assert.equal(Model.chargeThresholdActive(device, true, states), false)
  }
})

test('unplugged, absent, and fully charged batteries retain their behavior', () => {
  const unplugged = { ...battery, state: states.Discharging }
  assert.equal(Model.modeLabel(unplugged, true, states), 'On battery')
  assert.equal(Model.batteryIcon(unplugged, true, states), '󰂀')
  assert.equal(Model.batteryIcon({ isPresent: false }, false, states), '')
  const full = { ...battery, state: states.FullyCharged, percentage: 1 }
  assert.equal(Model.chargeThresholdActive(full, false, states), false)
  assert.equal(Model.modeLabel(full, false, states), 'Fully charged')
  assert.equal(Model.batteryIcon(full, false, states), '󰂅')
})
