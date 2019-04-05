# agricola
Implementation of agricola board game (revised edition) for training AI.
This repository is forked from "https://github.com/e2crawfo/agricola".

## Requirements


## Setting Up
* 'pip install -r requirements.txt'
* 'python setup.py install'

## Data Structure
* 草案段階
* 牧場は、一つの牧場を構成するマスの配列で表現される
* 職業、小進歩はIDで、アクションと大進歩は名前で表現される
* カード名、アクション名は大文字、残りは小文字
* どのような行動を求められているかはcurrent_eventで渡される
  * 家族のアクション、収穫、職業訓練など

* TODO
* 家畜管理
* ID to Name
* major_improvementを他と合わせる
```json
{
  "current_round" : 2,
  "current_player": 0,
  "current_event": "turn_start",
  "start_player": 0,
  "common_board": {
    "round_cards": [
      "MAJOR_IMPROVEMENT",
      "SHEEP",
      "FENCING",
      "SOW_BAKE",
      "FAMILY_GROWTH",
      "RENOVATION",
      "QUARRY_STAGE2",
      "VEGETABLE",
      "PIG",
      "CATTLE",
      "QUARRY_STAGE4",
      "PLOGH_SOW",
      "FAMILY_GROWTH_WITHOUT_ROOM",
      "RENOVATION_FENCING"
    ],
    "actions": [
      {
        "action_name": "WOOD_4",
        "resources": [
          {
            "resource_type": "wood",
            "resource_amount": 4
          }
        ]
      },
      {
        "action_type": "occupation_5players"
      }
    ],
    "remaining_major_improvements": [
      "FIREPLACE_2",
      "FIREPLACE_3",
      "COOKING_HEARTH_4",
      "COOKING_HEARTH_5",
      "WELL",
      "CLAY_OVEN",
      "STONE_OVEN",
      "JOINERY",
      "POTTERY",
      "BASKET_MAKER_WORKSHOP"
    ]
  },
  "players": [
    {
      "resources": {
        "food": 2,
        "wood": 0,
        "clay": 0,
        "stone": 0,
        "reed": 0,
        "sheep": 0,
        "boar": 0,
        "cattle": 0,
        "grain": 0,
        "vegitable": 0
      },
      "animal_placement": [
        {

        }
      ],
      "round_resources": [
        [
          {
            "resource_type": "food",
            "resource_amount": 2
          }
        ],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        []
      ],
      "board": [
        [[{ "object_type": "wooden_hut" }],[],[],[],[],[],[]],
        [[{ "object_type": "wooden_hut" }],[],[],[],[],[],[]],
        [[],[],[],[],[],[],[]]
      ],
      "pastures": [
        
          [[1,0], [2,0]]
        
      ],
      "played_major_improvements": [ "FIREPLACE_2" ],
      "played_minor_improvements": [{ "minor_improvement_id": 50}],
      "hand_minor_improvements": [100,101,102,103,104,105,106],
      "played_occupations": [{ "occupation_id": 50 }],
      "hand_occupations": [100,101,102,103,104,105,106],
      "families": [
        { "family_type": "in_house", "newborn": false }, 
        { "family_type": "in_house", "newborn": false }
      ]
    }
  ]
}
```