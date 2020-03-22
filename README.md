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
   "current_round":14,
   "current_player":2,
   "current_event":"",
   "start_player":2,
   "common_board":{  
      "round_cards":[  
         "MajorImprovement",
         "SheepMarket",
         "Fencing",
         "GrainUtilization",
         "BasicWishForChildren",
         "HouseRedevelopment",
         "WesternQuarry",
         "VegetableSeeds",
         "PigMarket",
         "EasternQuarry",
         "CattleMarket",
         "Cultivation",
         "UrgentWishForChildren",
         "FarmRedevelopment"
      ],
      "actions":[  
         {  
            "action_id":"MeetingPlace",
            "is_available":false,
            "taken_by":2
         },
         {  
            "action_id":"ClayPit",
            "resources":[  
               {  
                  "resource_type":"clay",
                  "resource_amount":0
               }
            ],
            "is_available":false,
            "taken_by":3
         },
         {  
            "action_id":"VegetableSeeds",
            "is_available":false,
            "taken_by":0
         },
         {  
            "action_id":"UrgentWishForChildren",
            "is_available":false,
            "taken_by":1
         },
         {  
            "action_id":"Grove",
            "resources":[  
               {  
                  "resource_type":"wood",
                  "resource_amount":0
               }
            ],
            "is_available":false,
            "taken_by":2
         },
         {  
            "action_id":"CattleMarket",
            "resources":[  
               {  
                  "resource_type":"cattle",
                  "resource_amount":0
               }
            ],
            "is_available":false,
            "taken_by":3
         },
         {  
            "action_id":"Hollow4P",
            "resources":[  
               {  
                  "resource_type":"clay",
                  "resource_amount":0
               }
            ],
            "is_available":false,
            "taken_by":0
         },
         {  
            "action_id":"EasternQuarry",
            "resources":[  
               {  
                  "resource_type":"stone",
                  "resource_amount":0
               }
            ],
            "is_available":false,
            "taken_by":1
         },
         {  
            "action_id":"FarmExpansion",
            "is_available":true
         },
         {  
            "action_id":"GrainSeeds",
            "is_available":true
         },
         {  
            "action_id":"Farmland",
            "is_available":true
         },
         {  
            "action_id":"DayLaborer",
            "is_available":true
         },
         {  
            "action_id":"Forest",
            "resources":[  
               {  
                  "resource_type":"wood",
                  "resource_amount":3
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"ReedBank",
            "resources":[  
               {  
                  "resource_type":"reed",
                  "resource_amount":1
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"Fishing",
            "resources":[  
               {  
                  "resource_type":"food",
                  "resource_amount":2
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"Lessons",
            "is_available":true
         },
         {  
            "action_id":"Copse",
            "resources":[  
               {  
                  "resource_type":"wood",
                  "resource_amount":2
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"ResourceMarket4P",
            "is_available":true
         },
         {  
            "action_id":"Lessons4P",
            "is_available":true
         },
         {  
            "action_id":"TravelingPlayers",
            "resources":[  
               {  
                  "resource_type":"food",
                  "resource_amount":7
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"MajorImprovement",
            "is_available":true
         },
         {  
            "action_id":"SheepMarket",
            "resources":[  
               {  
                  "resource_type":"sheep",
                  "resource_amount":1
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"Fencing",
            "is_available":true
         },
         {  
            "action_id":"GrainUtilization",
            "is_available":true
         },
         {  
            "action_id":"BasicWishForChildren",
            "is_available":true
         },
         {  
            "action_id":"HouseRedevelopment",
            "is_available":true
         },
         {  
            "action_id":"WesternQuarry",
            "resources":[  
               {  
                  "resource_type":"stone",
                  "resource_amount":1
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"PigMarket",
            "resources":[  
               {  
                  "resource_type":"boar",
                  "resource_amount":4
               }
            ],
            "is_available":true
         },
         {  
            "action_id":"Cultivation",
            "is_available":true
         },
         {  
            "action_id":"FarmRedevelopment",
            "is_available":true
         }
      ],
      "remaining_major_improvements":[  
         "Fireplace2",
         "Fireplace3",
         "CookingHearth4",
         "CookingHearth5",
         "Well",
         "ClayOven",
         "StoneOven",
         "Joinery",
         "Pottery",
         "BasketmakersWorkshop"
      ]
   },
   "players":[  
      {  
         "player_id":0,
         "resources":{  
            "food":9,
            "wood":20,
            "clay":10,
            "stone":4,
            "reed":6,
            "sheep":2,
            "boar":0,
            "cattle":0,
            "grain":1,
            "veg":2
         },
         "round_resources":{  

         },
         "board":[  
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  

               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ]
         ],
         "pastures":[  

         ],
         "played_improvements":[  

         ],
         "hand_improvements":[  
            "ButterChurn",
            "Lasso",
            "CarpentersParlor",
            "SleepingCorner",
            "StrawberryPatch",
            "AcornBasket",
            "CornScoop"
         ],
         "played_occupations":[  

         ],
         "hand_occupations":[  
            "Groom",
            "StableArchitect",
            "FirewoodCollector",
            "Manservant",
            "Conservator",
            "AssistantTiller",
            "Carpenter"
         ],
         "families":[  
            {  
               "family_type":"in_house",
               "newborn":false
            },
            {  
               "family_type":"in_house",
               "newborn":false
            }
         ],
         "score":-3
      },
      {  
         "player_id":1,
         "resources":{  
            "food":14,
            "wood":17,
            "clay":2,
            "stone":8,
            "reed":5,
            "sheep":5,
            "boar":1,
            "cattle":0,
            "grain":0,
            "veg":0
         },
         "round_resources":{  

         },
         "board":[  
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  

               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ]
         ],
         "pastures":[  

         ],
         "played_improvements":[  

         ],
         "hand_improvements":[  
            "HerringPot",
            "BigCountry",
            "DrinkingTrough",
            "BreadPaddle",
            "DutchWindmill",
            "MiningHammer",
            "ThreeFieldRotation"
         ],
         "played_occupations":[  

         ],
         "hand_occupations":[  
            "SheepWalker",
            "AnimalTamer",
            "Cottager",
            "WallBuilder",
            "RoughCaster",
            "Childless",
            "WoodCutter"
         ],
         "families":[  
            {  
               "family_type":"in_house",
               "newborn":false
            },
            {  
               "family_type":"in_house",
               "newborn":false
            },
            {  
               "family_type":"in_house",
               "newborn":false
            }
         ],
         "score":-2
      },
      {  
         "player_id":2,
         "resources":{  
            "food":8,
            "wood":10,
            "clay":8,
            "stone":5,
            "reed":3,
            "sheep":1,
            "boar":1,
            "cattle":2,
            "grain":2,
            "veg":1
         },
         "round_resources":{  

         },
         "board":[  
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  

               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ]
         ],
         "pastures":[  

         ],
         "played_improvements":[  

         ],
         "hand_improvements":[  
            "Basket",
            "MilkJug",
            "Loom",
            "Handplow",
            "SheperdsCrook",
            "Bottles",
            "Pitchfork"
         ],
         "played_occupations":[  

         ],
         "hand_occupations":[  
            "HedgeKeeper",
            "Stonecutter",
            "SmallScaleFarmer",
            "Pastor",
            "Priest",
            "StorehouseKeeper",
            "Consultant"
         ],
         "families":[  
            {  
               "family_type":"in_house",
               "newborn":false
            },
            {  
               "family_type":"in_house",
               "newborn":false
            },
            {  
               "family_type":"in_house",
               "newborn":false
            }
         ],
         "score":4
      },
      {  
         "player_id":3,
         "resources":{  
            "food":12,
            "wood":32,
            "clay":22,
            "stone":1,
            "reed":5,
            "sheep":4,
            "boar":0,
            "cattle":2,
            "grain":1,
            "veg":0
         },
         "round_resources":{  

         },
         "board":[  
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  
                  "object_type":"wooden_hut"
               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ],
            [  
               {  

               },
               {  

               },
               {  

               },
               {  

               },
               {  

               }
            ]
         ],
         "pastures":[  

         ],
         "played_improvements":[  

         ],
         "hand_improvements":[  
            "SackCart",
            "ClearingSpade",
            "LoamPit",
            "StoneTongs",
            "LumberMill",
            "ThreshingBoard",
            "Scullery"
         ],
         "played_occupations":[  

         ],
         "hand_occupations":[  
            "Lutenist",
            "Grocer",
            "SheepWhisperer",
            "Harpooner",
            "Tutor",
            "OrganicFarmer",
            "Geologist"
         ],
         "families":[  
            {  
               "family_type":"in_house",
               "newborn":false
            },
            {  
               "family_type":"in_house",
               "newborn":false
            }
         ],
         "score":-2
      }
   ]
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
  "action_id": "FarmExpansion",
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
  "aciton_id": "MeetingPlace",
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
  "action_id": "AnimalMarket",
  "animal_type": "sheep"
}
```

### 3人戦資材(?)
```json
{
  "action_id": "ResourceMarket3P",
  "resource_type": "reed"
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

```json
{
  "action_id": "GrainUtilization",
  "plant_grain_count": 1,
  "plant_vegitable_count": 1,
  "bake_grain_count": 1
}
```

↑現在の実装
⬇️は理想案

* sowingは畑のある位置を指定
* bakingは焼くのに使う進歩を指定
```json
{
  "action_id": "GrainUtilization",
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
  "action_id": "HouseRedevelopment",
  "material": "clay",
  "improvement": {
    "id": "FIELD",
    "position": [3, 0]
  }
}
```

### 増員進歩
```json
{
  "action_id": "BasicWishForChildren",
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

```json
{
  "actoin_id": "Cultivation",
  "ploughing_space" : [3,0],
  "plant_grain_count": 1,
  "plant_vegitable_count": 1
}
```

↑現在の実装
⬇️は理想案

``` json
{
  "actoin_id": "Cultivation",
  "ploughing_space" : [3,0],
  "sowing": [
    {
      "position": [0, 3],
      "seed": "VEGITABLE"
    }
  ]
}
```

### 改築柵
``` json
{
  "actoin_id": "FarmRedevelopment",
  "material": "clay",
  "pastures": [
    [[3,0]],[[4,0]],[[3,1],[4,1],[3,2],[4,2]]
  ]
}
```
