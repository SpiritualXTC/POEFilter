# POEFilter
Auto-Generation of an item-filter file used by the game Path of Exile.

Structured JSON file can be used to control the auto-generation for array expansions,
"cascading" action definitions, and colour constants.

## Version 0.1
Expect many many many bugs :)
Testing has so-far been rather rudimentary ... lol

## Description:
Item Filtering in Path of Exile is extremely helpful, with the high drop rates ... of very useless crap. The 
screen can be become rather cluttered very quickly.

Manually making an item filter has slowly become unweildly as Grinding Gear Games have been adding new features to the core game,
increasing the number of items/etc in the game while also including new functionality for filtering.
Keeping the look consistent across all items has gradually become harder...

So the idea for this project is to make constructing a filter ever-so-slightly easier.
Filter options will still need to be defined in the JSON file, but actions will be easier to manage across a large filter

## Features
* Support for item-filter functionality upto POE 3.5 (Betrayal League)
	(Including MiniMapIcon and PlayEffect)
* 100% JSON Loader
* Cascading action "styles"
	- Allows multiple filters to reuse an action "styles"
	- Allows a single filter to combine multiple "styles" (See Example Below)
* Action name expansion
	- Allows the action to be set based on properties from the filter expansion
	- Custom properties for action name expansion
* Filter Expansion
	- A group of filters with mostly the same conditions can be generated with a simple JSON objec
* Colour Constants


# TODO:
* Support for PlayAlertSound/PlayAlertSoundPositional/DisableAlertSound/CustomAlertSound
* Planned support for a file loader that will parse a file that resembles a standard filter, however
with changes allowing for the filter expansions and action cascading
* Action overrides defined directly from the filter
* Support for python creation: Ability to create an item filter from Python Scripting (only for the brave :P)
* Inherit / Override sub properties of an action [IE: the MiniMapIcon size, without affecting the colour or shape]




## Example (Coming Soon, in the meantime look in the **Filters** folder for testing examples

### Example 1: Corrupted Uniques (To be honest this hasn't been tested :P)
This is a fairly trivial example.
The result will generate an item filter with 2 entries.
The first one for corrupted uniques, that shares the same actions as non-corrupted uniques, however with a red border, and a red ground effect.
```json
{
	"colours":
	{
		"bg-default": {"r": 0, "g": 0, "b": 0, "a": 192},
		"unique": {"r": 175, "g": 96, "b": 37, "a": 255},
		"corrupted": {"r": 210, "g": 0, "b": 0, "a": 255}
	},
	"action":
	{
		"Unique":
		{
			"SetBorderColor": "{unique}",
			"SetTextColor": "{unique}",
			"SetBackgroundColor": "{bg-default}",
			"MiniMapIcon": {"Size": 0, "Colour": "Yellow", "Shape": "Star"},
			"PlayEffect": "Yellow"
		},
		"Corrupted":
		{
			"SetBorderColor": "{corrupted}",
			"PlayEffect": "Red"
		}
	},
	"filter":
	{
		"corrupted-unique":
		{
			"Rarity": "Unique",
			"Corrupted": "True",
			"action": [["Corrupted", "Unique"]]
		},
		"unique":
		{
			"Rarity": "Unique",
			"action": ["Unique"] 
		}
	}
}
```
Note: The twin brackets -[[- around the action are required so it doesn't expand the filter
Note 2: After boolean conditions generate properties, this could be condensed into a single option

### Example 2: TODO: Action name expansion
Also fairly trivial example.
The resulting filter will contain separate entries for 


### Example 3: TODO: Filter Expansion, with custom properties for action name expansion


- [x] Action Cascading
- [x] Filter Expansion
- [x] Support for Border/Background/Text item colouring
- [x] Support for MiniMapIcon features
- [x] Support for PlayEffect features
- [x] Support for action name-expansion (with custom properties)
- [ ] Support for AlertSound features
- [ ] Boolean Conditions automatically generating a property for action name expansion 




