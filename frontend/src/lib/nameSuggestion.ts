// Pre-fills the character name from the username (docs/09-roadmap.md, M1).
// Only a suggestion: the player can change it and the server validates it.

const MIN_LENGTH = 3;
const MAX_LENGTH = 20;

/**
 * Usernames allow digits, "_" and "-", character names do not:
 * "_" and "-" become spaces, digits are dropped, each word starts upper-case.
 * Returns "" when nothing usable (at least 3 characters) remains.
 */
export function suggestCharacterName(username: string): string {
	const words = username
		.replace(/[_-]+/g, ' ')
		.replace(/[0-9]+/g, '')
		.split(' ')
		.filter(Boolean)
		.map((w) => w.charAt(0).toUpperCase() + w.slice(1));
	const name = words.join(' ').slice(0, MAX_LENGTH).trim();
	return name.length >= MIN_LENGTH ? name : '';
}
