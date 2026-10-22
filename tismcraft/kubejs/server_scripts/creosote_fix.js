ServerEvents.recipes(event => {
  event.remove({
    type: 'create:filling',
    output: 'immersiveengineering:treated_wood_horizontal'
  })
})