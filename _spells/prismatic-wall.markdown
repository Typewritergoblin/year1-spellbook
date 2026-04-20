---
layout: post
title:  "Prismatic Wall"
sources: [PHB 2024]
tags: [bard, wizard, level9, action, abjuration]
---

**9th-level abjuration**

**Casting Time**: 1 action

**Range**: 60 feet

**Components**: V, S

**Duration**: 10 minutes

A shimmering, multicolored plane of light forms a vertical opaque wall—up to 90 feet long, 30 feet high, and 1 inch thick—centered on a point within range. Alternatively, you shape the wall into a globe up to 30 feet in diameter centered on a point within range. The wall lasts for the duration. If you position the wall in a space occupied by a creature, the spell ends instantly without effect.

The wall sheds &amp;Reference[BrightLight] within 100 feet and &amp;Reference[DimLight] for an additional 100 feet. You and creatures you designate when you cast the spell can pass through and be near the wall without harm. If another creature that can see the wall moves within 20 feet of it or starts its turn there, the creature must succeed on a Constitution saving throw or have the &amp;Reference[Blinded apply=false] condition for 1 minute.

The wall consists of seven layers, each with a different color. When a creature reaches into or passes through the wall, it does so one layer at a time through all the layers. Each layer forces the creature to make a Dexterity saving throw or be affected by that layer’s properties as described in the Prismatic Layers table.

The wall, which has AC 10, can be destroyed one layer at a time, in order from red to violet, by means specific to each layer. If a layer is destroyed, it is gone for the duration. *@UUID[Compendium.dnd-players-handbook.spells.Item.phbsplAntimagicF]{Antimagic Field}* has no effect on the wall, and *@UUID[Compendium.dnd-players-handbook.spells.Item.phbsplDispelMagi]{Dispel Magic}* can affect only the violet layer.

Prismatic LayersOrderEffects1**Red.** *Failed Save:* 12d6 Fire damage. *Successful Save:* Half as much damage. *Additional Effects*: Nonmagical ranged attacks can’t pass through this layer, which is destroyed if it takes at least 25 Cold damage.2**Orange.** *Failed Save:* 12d6 Acid damage. *Successful Save:* Half as much damage. *Additional Effects:* Magical ranged attacks can’t pass through this layer, which is destroyed by a strong wind (such as the one created by *@UUID[Compendium.dnd-players-handbook.spells.Item.phbsplGustofWind]{Gust of Wind}*).3**Yellow.** *Failed Save:* 12d6 Lightning damage. *Successful Save:* Half as much damage. *Additional Effects:* The layer is destroyed if it takes at least 60 Force damage.4**Green.** *Failed Save:* 12d6 Poison damage. *Successful Save:* Half as much damage. *Additional Effects:* A *@UUID[Compendium.dnd-players-handbook.spells.Item.phbsplPasswall00]{Passwall}* spell, or another spell of equal or greater level that can open a portal on a solid surface, destroys this layer.5**Blue.** *Failed Save:* 12d6 Cold damage. *Successful Save:* Half as much damage. *Additional Effects:* The layer is destroyed if it takes at least 25 Fire damage.6**Indigo.** *Failed Save:* The target has the &amp;Reference[Restrained apply=false] condition and makes a [[/save ability=con dc=@attributes.spell.dc format=long]] at the end of each of its turns. If it successfully saves three times, the condition ends. If it fails three times, it has the &amp;Reference[Petrified] condition until it is freed by an effect like the *@UUID[Compendium.dnd-players-handbook.spells.Item.phbsplGreaterRes]{Greater Restoration}* spell. The successes and failures needn’t be consecutive; keep track of both until the target collects three of a kind. *Additional Effects:* Spells can’t be cast through this layer, which is destroyed by Bright Light shed by the *@UUID[Compendium.dnd-players-handbook.spells.Item.phbsplDaylight00]{Daylight}* spell.7**Violet.** *Failed Save:* The target has the &amp;Reference[Blinded apply=false] condition and makes a [[/save ability=wis dc=@attributes.spell.dc format=long]] at the start of your next turn. On a successful save, the condition ends. On a failed save, the condition ends, and the creature teleports to another plane of existence (DM’s choice). *Additional Effects:* This layer is destroyed by *@UUID[Compendium.dnd-players-handbook.spells.Item.phbsplDispelMagi]{Dispel Magic}*.
