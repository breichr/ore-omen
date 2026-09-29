// Display-only mirror of creation rules (docs/01-welt.md) so the form can guide
// the player. The server validates everything again (backend/app/game/character.py).

export const CLASSES = ['gunslinger', 'prospector', 'quack', 'preacher', 'bounty_hunter'] as const;
export const ATTRIBUTES = ['strength', 'dexterity', 'intellect', 'charisma'] as const;
export const ATTRIBUTE_START_VALUE = 5;
export const ATTRIBUTE_START_FREE_POINTS = 4;
