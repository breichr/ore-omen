// All UI texts in one place (docs/08-technik.md, "Entschieden" 4).
// Codes (classes, attributes, error codes) come from the API in English.

export const de = {
	app: {
		name: 'Ore & Omen',
		tagline: 'Grab tief. Bleib menschlich.',
		loading: 'Einen Moment …',
		retry: 'Nochmal versuchen'
	},

	offline: {
		banner: 'Keine Verbindung. Der Spielstand braucht Netz.',
		page: 'Der Telegraf schweigt. Ohne Verbindung kommt keine Nachricht aus Hollow Creek.'
	},

	install: {
		button: 'App installieren',
		iosHint: 'Zum Installieren: Teilen-Symbol antippen, dann „Zum Home-Bildschirm“.',
		dismiss: 'Später'
	},

	auth: {
		loginTitle: 'Anmelden',
		registerTitle: 'Neu in Hollow Creek',
		loginIntro: 'Der Bahnsteig ist leer. Jemand hat deinen Namen ins Gästebuch geschrieben.',
		registerIntro:
			'Der letzte Zug, der noch fährt. Der Schaffner nimmt dein Ticket und sieht dich zu lange an.',
		email: 'E-Mail',
		password: 'Passwort',
		passwordHint: 'Mindestens 8 Zeichen.',
		login: 'Anmelden',
		register: 'Konto anlegen',
		logout: 'Abmelden',
		toRegister: 'Noch kein Konto? Hier einsteigen.',
		toLogin: 'Schon ein Konto? Anmelden.'
	},

	create: {
		title: 'Wer steigt aus?',
		intro:
			'Der Zug hält. Als du dich umdrehst, ist das Abteil gegenüber leer. Der Schaffner ist fort.',
		name: 'Name',
		nameHint: '3–20 Zeichen: Buchstaben, Leerzeichen, Bindestrich, Apostroph.',
		classTitle: 'Klasse',
		ability: 'Duellfähigkeit',
		attributesTitle: 'Attribute',
		attributesIntro: 'Jedes Attribut beginnt bei 5. Verteile 4 weitere Punkte.',
		pointsLeft: (n: number) => (n === 1 ? 'Noch 1 Punkt' : `Noch ${n} Punkte`),
		increase: (label: string) => `${label} erhöhen`,
		decrease: (label: string) => `${label} senken`,
		submit: 'Aussteigen'
	},

	yard: {
		title: 'Dein Hof',
		level: (n: number) => `Stufe ${n}`,
		dollars: (n: number) => `${n.toLocaleString('de-DE')} $`,
		emptyTitle: 'Eine Parzelle am Stadtrand',
		empty:
			'Festgetretene Erde, ein Pflock mit deiner Nummer, sonst nichts. Kein Zelt, kein Zaun. Nachts hört man die Mine atmen.',
		comingSoon: 'Bauen und Arbeiten kommen mit dem nächsten Zug.'
	},

	classes: {
		gunslinger: {
			name: 'Revolverheld',
			role: 'Duellspezialist',
			ability: 'Fächerschuss: 2 Schüsse in einem Zug, je −10 %.'
		},
		prospector: {
			name: 'Prospektor',
			role: 'Erzabbau, Fallen',
			ability: 'Staubwolke: nächster gegnerischer Schuss −25 %.'
		},
		quack: {
			name: 'Quacksalber',
			role: 'Tinkturen, Heilung, Gifte',
			ability: 'Tinktur: +20 Leben statt Schuss.'
		},
		preacher: {
			name: 'Prediger',
			role: 'Segen, Bannkreise',
			ability: 'Segen: erster erhaltener Treffer −30 % Schaden.'
		},
		bounty_hunter: {
			name: 'Kopfgeldjäger',
			role: 'Spuren, Kopfgelder',
			ability: 'Fährte: sieht die Taktik des Gegners; +10 % Treffer gegen Gesuchte.'
		}
	} as Record<string, { name: string; role: string; ability: string }>,

	attributes: {
		strength: { name: 'Stärke', hint: 'Zähigkeit, Tragen, Bauarbeit' },
		dexterity: { name: 'Geschick', hint: 'Zielen, Reflexe, Schlösser' },
		intellect: { name: 'Verstand', hint: 'Instinkt, Handwerk, Kartenkunde' },
		charisma: { name: 'Charisma', hint: 'Nerven, Handel, Überreden' }
	} as Record<string, { name: string; hint: string }>,

	regions: {
		hollow_creek: 'Hollow Creek'
	} as Record<string, string>,

	errors: {
		not_authenticated: 'Bitte melde dich an.',
		invalid_credentials: 'E-Mail oder Passwort stimmt nicht.',
		email_taken: 'Mit dieser E-Mail gibt es schon ein Konto.',
		rate_limited: 'Zu viele Versuche. Warte eine Minute.',
		character_exists: 'Du hast bereits einen Charakter.',
		name_taken: 'Diesen Namen trägt schon jemand in Hollow Creek.',
		name_length: 'Der Name muss 3 bis 20 Zeichen lang sein.',
		name_chars: 'Erlaubt sind Buchstaben, Leerzeichen, Bindestrich und Apostroph.',
		unknown_class: 'Bitte wähle eine Klasse.',
		points_not_spent: 'Verteile genau 4 Punkte.',
		negative_points: 'Punkte können nicht negativ sein.',
		unknown_attribute: 'Unbekanntes Attribut.',
		validation: 'Bitte prüfe deine Eingaben.',
		network: 'Keine Verbindung zum Server.',
		unknown: 'Etwas ist schiefgelaufen. Versuch es nochmal.'
	} as Record<string, string>
};

export function errorText(code: string): string {
	return de.errors[code] ?? de.errors.unknown;
}
