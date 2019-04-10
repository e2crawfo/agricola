# agricola
Implementation of agricola board game (revised edition) for training AI.
This repository is forked from "https://github.com/e2crawfo/agricola".

## Execution
```shell
sh run.sh
```

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
      "SOWING_BAKING",
      "FAMILY_GROWTH",
      "RENOVATION",
      "QUARRY_STAGE2",
      "VEGETABLE",
      "PIG",
      "CATTLE",
      "QUARRY_STAGE4",
      "PLOGH_SOWING",
      "FAMILY_GROWTH_WITHOUT_ROOM",
      "RENOVATION_FENCING"
    ],
    "actions": [
      {
        "action_id": "WOOD_4",
        "resources": [
          {
            "resource_type": "wood",
            "resource_amount": 4
          }
        ],
        "is_available": true
      },
      {
        "action_id": "occupation_5players",
        "is_available": false
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
      "played_improvements": [{ "improvement_id": "ID"}, { "improvement_id": "FIREPLACE_2" }],
      "hand_improvements": ["ID1","ID2","ID3","ID4","ID5","ID6","ID7"],
      "played_occupations": [{ "occupation_id": "ID" }],
      "hand_occupations": ["ID1","ID2","ID3","ID4","ID5","ID6","ID7"],
      "families": [
        { "family_type": "in_house", "newborn": false }, 
        { "family_type": "in_house", "newborn": false }
      ]
    }
  ]
}
```

## Sample Input
```json
{
    "common_board": {
        "actions": [
            {
                "action_id": "ROOM_STABLE_BUILDINGS",
                "is_available": true
            },
            {
                "action_id": "STARTING_PLAYER",
                "is_available": true
            },
            {
                "action_id": "GRAIN",
                "is_available": true
            },
            {
                "action_id": "PLOUGH",
                "is_available": true
            },
            {
                "action_id": "DAY_LABORER",
                "is_available": true
            },
            {
                "action_id": "WOOD_3",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 3,
                        "resource_type": "wood"
                    }
                ]
            },
            {
                "action_id": "CLAY_1",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 1,
                        "resource_type": "clay"
                    }
                ]
            },
            {
                "action_id": "REED_1",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 1,
                        "resource_type": "reed"
                    }
                ]
            },
            {
                "action_id": "FISHING",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 1,
                        "resource_type": "food"
                    }
                ]
            },
            {
                "action_id": "OCCUPATION",
                "is_available": true
            },
            {
                "action_id": "WOOD_1",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 1,
                        "resource_type": "wood"
                    }
                ]
            },
            {
                "action_id": "WOOD_2",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 2,
                        "resource_type": "wood"
                    }
                ]
            },
            {
                "action_id": "REED_STONE_FOOD",
                "is_available": true
            },
            {
                "action_id": "CLAY_2",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 2,
                        "resource_type": "clay"
                    }
                ]
            },
            {
                "action_id": "OCCUPATION_4P",
                "is_available": true
            },
            {
                "action_id": "TRAVELING_PLAYERS",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 1,
                        "resource_type": "food"
                    }
                ]
            },
            {
                "action_id": "SHEEP",
                "is_available": true,
                "resources": [
                    {
                        "resource_amount": 1,
                        "resource_type": "sheep"
                    }
                ]
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
        ],
        "round_cards": [
            "SHEEP",
            "MAJOR_IMPROVEMENT",
            "FENCING",
            "SOWING_BAKING",
            "FAMILY_GROWTH",
            "QUARRY_STAGE2",
            "RENOVATION",
            "PIG",
            "VEGITABLE",
            "CATTLE",
            "QUARRY_STAGE4",
            "FAMILY_GROWTH_WITHOUT_ROOM",
            "PLOGH_SOWING",
            "RENOVATION_FENCING"
        ]
    },
    "current_event": "",
    "current_player": 2,
    "current_round": 1,
    "players": [
        {
            "board": [
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [],
                    [],
                    [],
                    [],
                    []
                ]
            ],
            "families": [
                {
                    "family_type": "in_house",
                    "newbord": false
                },
                {
                    "family_type": "in_house",
                    "newbord": false
                }
            ],
            "hand_improvements": [
                "PondHut",
                "Brook",
                "ClearingSpade",
                "ShiftingCultivation",
                "Lasso",
                "Caravan",
                "SackCart"
            ],
            "hand_occupations": [
                "AnimalTamer",
                "Stonecutter",
                "OrganicFarmer",
                "Geologist",
                "Greengrocer",
                "AnimalDealer",
                "FrameBuilder"
            ],
            "pastures": [],
            "played_improvements": [],
            "played_occupations": [],
            "resources": {
                "boar": 0,
                "cattle": 0,
                "clay": 0,
                "food": 0,
                "grain": 0,
                "reed": 0,
                "sheep": 0,
                "stone": 0,
                "veg": 0,
                "wood": 0
            },
            "round_resources": {}
        },
        {
            "board": [
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [],
                    [],
                    [],
                    [],
                    []
                ]
            ],
            "families": [
                {
                    "family_type": "in_house",
                    "newbord": false
                },
                {
                    "family_type": "in_house",
                    "newbord": false
                }
            ],
            "hand_improvements": [
                "ClayEmbankment",
                "Loom",
                "BreadPaddle",
                "YoungAnimalMarket",
                "StrawberryPatch",
                "Claypipe",
                "Beanfield"
            ],
            "hand_occupations": [
                "Lutenist",
                "SmallScaleFarmer",
                "Carpenter",
                "Conjurer",
                "FirewoodCollector",
                "StableArchitect",
                "Priest"
            ],
            "pastures": [],
            "played_improvements": [],
            "played_occupations": [],
            "resources": {
                "boar": 0,
                "cattle": 0,
                "clay": 0,
                "food": 0,
                "grain": 0,
                "reed": 0,
                "sheep": 0,
                "stone": 0,
                "veg": 0,
                "wood": 0
            },
            "round_resources": {}
        },
        {
            "board": [
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [],
                    [],
                    [],
                    [],
                    []
                ]
            ],
            "families": [
                {
                    "family_type": "in_house",
                    "newbord": false
                },
                {
                    "family_type": "in_house",
                    "newbord": false
                }
            ],
            "hand_improvements": [
                "JunkRoom",
                "CarpentersParlor",
                "MiningHammer",
                "Basket",
                "Bottles",
                "AcornBasket",
                "SheperdsCrook"
            ],
            "hand_occupations": [
                "Consultant",
                "SeasonalWorker",
                "Braggart",
                "PigBreeder",
                "PaperMaker",
                "BrushwoodCollector",
                "ScytheWorker"
            ],
            "pastures": [],
            "played_improvements": [],
            "played_occupations": [],
            "resources": {
                "boar": 0,
                "cattle": 0,
                "clay": 0,
                "food": 0,
                "grain": 0,
                "reed": 0,
                "sheep": 0,
                "stone": 0,
                "veg": 0,
                "wood": 0
            },
            "round_resources": {}
        },
        {
            "board": [
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [
                        {
                            "object_type": "wooden_hut"
                        }
                    ],
                    [],
                    [],
                    [],
                    []
                ],
                [
                    [],
                    [],
                    [],
                    [],
                    []
                ]
            ],
            "families": [
                {
                    "family_type": "in_house",
                    "newbord": false
                },
                {
                    "family_type": "in_house",
                    "newbord": false
                }
            ],
            "hand_improvements": [
                "MilkJug",
                "Scullery",
                "DrinkingTrough",
                "MoldboardPlow",
                "HardPorcelain",
                "Manger",
                "ButterChurn"
            ],
            "hand_occupations": [
                "Harpooner",
                "Childless",
                "AssistantTiller",
                "SheepWhisperer",
                "MasterBricklayer",
                "PlowDriver",
                "HedgeKeeper"
            ],
            "pastures": [],
            "played_improvements": [],
            "played_occupations": [],
            "resources": {
                "boar": 0,
                "cattle": 0,
                "clay": 0,
                "food": 0,
                "grain": 0,
                "reed": 0,
                "sheep": 0,
                "stone": 0,
                "veg": 0,
                "wood": 0
            },
            "round_resources": {}
        }
    ],
    "start_player": 2
}
```

## Output format
### common
```json
{
  "action_id": "wood_4"
}
```

### 増築、厩
* roomsとstablesを[x, y]の配列で渡す
```json
{
  "action_id": "ROOM_STABLE_BUILDINGS",
  "rooms": [
    [0, 3]
  ],
  "stables": [
    []
  ]
}
```

### スタプレ
* minor_improvementをプレイする際の付加情報はminor_improvementの中に記載する
* スタプレ取らずの場合はdont_take_starting_playerをtrueとする
```json
{
  "aciton_id": "STARTING_PLAYER",
  "dont_take_starting_player": true,
  "improvement": {
    "id": "FIELD",
    "position": [3, 0]
  }
}
```

### 小麦
```json
{
  "action_id": "GRAIN"
}
```

### 畑
* TODO 鋤はどうする？
```json
{
  "action_id": "PLOUGH",
  "position": [3, 0]
}
```

### 日雇い
```json
{
  "action_id": "DAY_LABOROR"
}
```

### 木
```json
{
  "action_id": "WOOD_4"
}
```

### レンガ
```json
{
  "action_id": "CLAY_3"
}
```

### 葦
```json
{
  "action_id": "REED_1"
}
```

### 葦石木
```json
{
  "action_id": "REED_STONE_WOOD"
}
```

### 漁
```json
{
  "aciton_id": "FISHING"
}
```

### 増員、職業(5Player)
* 増員の場合はoccupation_idを渡さない
```json
{
  "action_id": "OCCUPATION_OR_FAMILY_GROWTH",
  "occupation_id": "WOODCUTTER"
}
```

### 増築、小劇場
* 小劇場の場合は座標を渡さない
```json
{
  "action_id": "ROOM_BUILDING_OR_TRAVELING_PLAYERS",
  "position": [3, 0]
}
```

### 家畜
```json
{
  "action_id": "ANIMALS",
  "acnimal_type": "SHEEP"
}
```

### 職業
```json
{
  "action_id": "OCCUPATION",
  "occupation_id": "WOODCUTTER"
}
```

### 羊
```json
{
  "actoin_id": "SHEEP"
}
```

### 種パン
* sowingは畑のある位置を指定
* bakingは焼くのに使う進歩を指定
```json
{
  "action_id": "SOWING_BAKING",
  "sowing": [
    {
      "position": [0,3],
      "seed": "VEGITABLE"
    }
  ],
  "baking": [
    {
      "baking_improvement": "FIREPLACE_2"
    }
  ]
}
```

### 大進歩、小進歩
```json
{
  "action_id": "MAJOR_IMPROVEMENT",
  "id": "FIELD",
  "position": [3, 0]
}
```

### 柵
* 新規で囲う牧場を指定する
```json
{
  "action_id": "FENCING",
  "pastures": [
    [[3,0]],[[4,0]],[[3,1],[4,1],[3,2],[4,2]]
  ]
}
```

### 改築進歩
```json
{
  "action_id": "RENOVATION",
  "improvement": {
    "id": "FIELD",
    "position": [3, 0]
  }
}
```

### 増員進歩
```json
{
  "action_id": "FAMILY_GROWTH",
  "improvement": {
    "id": "FIELD",
    "position": [3, 0]
  }
}
```

### 増員進歩
```json
{
  "action_id": "FAMILY_GROWTH",
  "improvement": {
    "id": "FIELD",
    "position": [3, 0]
  }
}
```


### 家なし増員
```json
{
  "action_id": "FAMILY_GROWTH_WITHOUT_ROOM"
}
```

### 畑種
``` json
{
  "actoin_id": "PLOGH_SOWING",
  "plogh" : [3,0],
  "sowing": [
    {
      "position": [0, 3],
      "seed": "VEGITABLE"
    }
  ],
}
```

### 改築柵
``` json
{
  "actoin_id": "RENOVATION_FENCING",
  "pastures": [
    [[3,0]],[[4,0]],[[3,1],[4,1],[3,2],[4,2]]
  ]
}
```
