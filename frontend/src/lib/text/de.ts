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

	landing: {
		intro:
			'Hollow Creek, 1878. Unter der Stadt liegt ein schwarzes Erz, das Menschen Dinge können lässt, die sie nicht können sollten. Es verlangt einen Preis.',
		points: [
			'Bau deine Parzelle vom Zelt zum Gehöft.',
			'Schließ dich einer von vier Fraktionen an – und mach dir die anderen zu Feinden.',
			'Duelliere dich, jage Kopfgelder, oder werde selbst gejagt.',
			'Wenige Minuten am Tag. Timer laufen weiter, während du weg bist.'
		],
		register: 'Einsteigen',
		login: 'Ich bin schon in der Stadt'
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
		username: 'Benutzername',
		usernameHint:
			'3–20 Zeichen: Buchstaben, Ziffern, _ und -. Nur zum Anmelden, nicht dein Charaktername.',
		password: 'Passwort',
		passwordHint: 'Mindestens 8 Zeichen.',
		login: 'Anmelden',
		register: 'Konto anlegen',
		logout: 'Abmelden',
		toRegister: 'Noch kein Konto? Hier einsteigen.',
		toLogin: 'Schon ein Konto? Anmelden.',
		toRecover: 'Passwort vergessen? Mit Notfallschlüssel wiederherstellen.'
	},

	settings: {
		title: 'Einstellungen',
		link: 'Einstellungen',
		back: 'Zurück zum Hof',
		account: (name: string) => `Angemeldet als ${name}`,
		keyTitle: 'Notfallschlüssel',
		keyIntro:
			'Erzeugt einen neuen Schlüssel. Der alte gilt danach nicht mehr. Zur Bestätigung brauchst du dein Passwort.',
		keySubmit: 'Neuen Schlüssel erzeugen'
	},

	recovery: {
		title: 'Wiederherstellen',
		intro:
			'Mit deinem Notfallschlüssel setzt du ein neues Passwort. Danach bekommst du einen neuen Schlüssel.',
		key: 'Notfallschlüssel',
		keyPlaceholder: 'XXXXX-XXXXX-XXXXX-XXXXX-XXXXX',
		newPassword: 'Neues Passwort',
		submit: 'Passwort setzen',
		showTitle: 'Dein Notfallschlüssel',
		showNewTitle: 'Dein neuer Notfallschlüssel',
		showIntro:
			'Schreib ihn auf oder speichere ihn im Passwort-Manager. Er wird nur dieses eine Mal angezeigt. Ohne ihn kann ein vergessenes Passwort nicht zurückgesetzt werden.',
		showOldInvalid: 'Der alte Schlüssel gilt nicht mehr.',
		copy: 'Kopieren',
		copied: 'Kopiert',
		confirm: 'Ich habe den Schlüssel sicher notiert.',
		continue: 'Weiter'
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
		invalid_credentials: 'Benutzername oder Passwort stimmt nicht.',
		username_taken: 'Dieser Benutzername ist schon vergeben.',
		username_length: 'Der Benutzername muss 3 bis 20 Zeichen lang sein.',
		username_chars: 'Erlaubt sind Buchstaben ohne Umlaute, Ziffern, _ und -.',
		password_length: 'Das Passwort muss mindestens 8 Zeichen lang sein.',
		invalid_password: 'Das Passwort stimmt nicht.',
		invalid_recovery: 'Benutzername oder Notfallschlüssel stimmt nicht.',
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
