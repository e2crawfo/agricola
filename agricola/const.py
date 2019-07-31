
from .utils import dotDict, recDotDict

event_sources = dotDict({
  'game': 'game',
  'plough': 'plough',
})

trigger_event_names = dotDict({
  'start_round': 'start_round',
  'start_stage': 'start_stage',
  'end_round': 'end_round',
  'end_stage': 'end_stage',
  'field_phase': 'field_phase',
  'feeding_phase': 'feeding_phase',
  'breeding_phase': 'breeding_phase',
  'renovation': 'renovation',
  'build_room': 'build_room',
  'build_pasture': 'build_pasture',
  'build_stable': 'build_stable',
  'plow_field': 'plow_field',
  'birth': 'birth',
  'occupation': 'occupation',
  'minor_improvement': 'minor_improvement',
  'major_improvement': 'major_improvement',
  "take_resources_from_action": "take_resources_from_action",
  "resource_payment_renovation": "resource_payment_renovation",
  "resource_trading": "resource_trading",
})