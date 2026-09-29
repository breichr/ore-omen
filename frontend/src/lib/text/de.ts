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

	resources: {
		wood: 'Holz',
		iron: 'Eisen',
		cattle: 'Vieh',
		whiskey: 'Whiskey',
		silver: 'Silber',
		salt: 'Salz',
		black_ore: 'Schwarzerz',
		dollars: '$'
	} as Record<string, string>,

	mainHouse: {
		tent: 'Zelt',
		hut: 'Hütte',
		log_house: 'Blockhaus',
		ranch_house: 'Ranchhaus',
		manor: 'Herrenhaus'
	} as Record<string, string>,

	categories: {
		core: 'Kern',
		production: 'Produktion',
		character: 'Charakter & Klassen',
		defense: 'Verteidigung',
		supernatural: 'Übernatürlich'
	} as Record<string, string>,

	settlement: {
		storage: (cap: number) => `Lager: ${cap.toLocaleString('de-DE')} je Ressource`,
		perHour: (n: number) => `+${n}/h`,
		full: 'voll',
		queueTitle: 'Im Bau',
		queueEmpty: 'Gerade wird nichts gebaut.',
		slots: (used: number, total: number) => `${used}/${total} Bauplätze`,
		buildingsTitle: 'Gebäude',
		moreBuildings: (n: number) => `Weitere Gebäude (${n})`,
		level: (n: number) => `Stufe ${n}`,
		notBuilt: 'Noch nicht gebaut',
		build: 'Bauen',
		upgrade: (n: number) => `Ausbauen auf ${n}`,
		maxed: 'Höchste Stufe',
		cost: 'Kosten',
		duration: 'Dauer',
		produces: 'Produktion',
		cancel: 'Abbrechen',
		cancelConfirm: 'Bau abbrechen? Du bekommst die Hälfte der Kosten zurück.',
		lost: (text: string) => `Kein Platz im Lager, verfallen: ${text}`,
		upgradeTo: (name: string, n: number) => `${name} → Stufe ${n}`
	},

	jobs: {
		title: 'Arbeit',
		intro: 'Immer nur eine Arbeit auf einmal.',
		start: 'Anfangen',
		cancel: 'Aufhören',
		cancelConfirm: 'Aufhören? Du bekommst nichts dafür.',
		running: (name: string) => `Du arbeitest: ${name}`,
		done: (name: string) => `Fertig: ${name}`,
		overflow: (text: string) => `Lager zu voll, verfällt: ${text}`,
		xp: (n: number) => `${n} XP`
	},

	reasons: {
		main_house_too_low: 'Haupthaus zu niedrig',
		not_enough_resources: 'Zu wenig Ressourcen',
		queue_full: 'Alle Bauplätze belegt',
		already_building: 'Wird schon gebaut',
		excluded: 'Verträgt sich nicht mit einem anderen Gebäude',
		max_level: 'Höchste Stufe erreicht'
	} as Record<string, string>,

	progress: {
		xp: (have: number, need: number) =>
			`${have.toLocaleString('de-DE')} / ${need.toLocaleString('de-DE')} XP`,
		pointsAvailable: 'Du hast Punkte zu verteilen.',
		distribute: 'Jetzt verteilen'
	},

	points: {
		title: 'Charakter',
		back: 'Zurück zum Hof',
		attributesTitle: 'Attribute',
		skillsTitle: 'Skills',
		freeAttributes: (n: number) => (n === 1 ? '1 Attributpunkt frei' : `${n} Attributpunkte frei`),
		freeSkills: (n: number) => (n === 1 ? '1 Skillpunkt frei' : `${n} Skillpunkte frei`),
		cap: (n: number) => `Höchstens ${n} Punkte pro Skill (Stufe + 2).`,
		duelValues: 'Duellwerte',
		duelValue: 'Duellwert',
		save: 'Übernehmen',
		reset: 'Zurücksetzen',
		saved: 'Gespeichert.'
	},

	skills: {
		toughness: 'Zähigkeit',
		building: 'Bauen',
		carrying: 'Tragen',
		aim: 'Zielen',
		reflexes: 'Reflexe',
		sleight_of_hand: 'Fingerfertigkeit',
		instinct: 'Instinkt',
		crafting: 'Handwerk',
		cartography: 'Kartenkunde',
		nerve: 'Nerven',
		trade: 'Handel',
		persuasion: 'Überreden'
	} as Record<string, string>,

	yard: {
		title: 'Dein Hof',
		level: (n: number) => `Stufe ${n}`,
		dollars: (n: number) => `${n.toLocaleString('de-DE')} $`,
		emptyTitle: 'Eine Parzelle am Stadtrand',
		empty:
			'Festgetretene Erde, ein Pflock mit deiner Nummer, sonst nichts. Kein Zelt, kein Zaun. Nachts hört man die Mine atmen.',
		firstStep: 'Fang mit einem Zelt an: Das Haupthaus bestimmt, wie hoch alles andere wachsen darf.'
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
		hollow_creek: 'Hollow Creek',
		pine_slope: 'Kiefernhang',
		deep_vein: 'Die Tiefe Ader',
		salt_flats: 'Salzebene',
		silent_mission: 'Stille Mission',
		the_gorge: 'Die Schlucht'
	} as Record<string, string>,

	nav: {
		yard: 'Hof',
		quests: 'Aufträge',
		factions: 'Fraktionen',
		character: 'Charakter'
	},

	factions: {
		company: 'Die Kompanie',
		order: 'Der Orden vom Letzten Licht',
		ash_gang: 'Die Aschenbande',
		keepers: 'Die Hüter der Schlucht'
	} as Record<string, string>,

	factionShort: {
		company: 'Kompanie',
		order: 'Orden',
		ash_gang: 'Aschenbande',
		keepers: 'Hüter'
	} as Record<string, string>,

	tiers: {
		hated: 'Verhasst',
		hostile: 'Feindselig',
		neutral: 'Neutral',
		known: 'Bekannt',
		respected: 'Geschätzt',
		trusted: 'Vertraut',
		honored: 'Ehrenrang'
	} as Record<string, string>,

	factionScreen: {
		title: 'Fraktionen',
		intro: 'Ruf bei einer Fraktion kostet Ruf bei anderen.',
		cap: (n: number) => `Deckel: ${n}`,
		oath: 'Treue schwören',
		oathConfirm: (name: string) =>
			`${name} die Treue schwören? Ein späterer Wechsel kostet die Hälfte deines Rufs dort.`,
		sworn: 'Du hast geschworen.',
		oathHint: 'Kompanie oder Aschenbande: Über 799 kommst du nur mit einem Treueschwur.'
	},

	questScreen: {
		title: 'Aufträge',
		here: (region: string) => `Du bist in ${region}.`,
		busy: 'Du bist beschäftigt.',
		activity: {
			job: 'Arbeit',
			quest: 'Unterwegs',
			travel: 'Reise',
			delay: 'Aufgehalten'
		} as Record<string, string>,
		open: 'Offen',
		openChoice: 'Wartet auf deine Entscheidung',
		openTraveling: 'Unterwegs',
		onboarding: 'Der letzte Zug',
		dailies: 'Tagesarbeiten',
		dailiesReset: (time: string) => `Neue Tagesarbeiten um ${time} Uhr.`,
		factionQuests: 'Fraktionsaufträge',
		none: 'Gerade nichts.',
		start: 'Aufbrechen',
		duration: (text: string) => `Dauer ${text}`,
		instant: 'sofort',
		travelTitle: 'Reisen',
		travelTo: (region: string) => `Nach ${region}`,
		travel: 'Reisen',
		fromRep: (tier: string) => `ab ${tier}`,
		onboardingHint: 'Der letzte Zug wartet noch auf dich.',
		reasons: {
			wrong_region: 'Anderswo',
			busy: 'Du bist beschäftigt',
			done_today: 'Heute erledigt',
			in_progress: 'Läuft',
			reputation_too_low: 'Ruf zu niedrig',
			gorge_closed: 'Erst ab Hüter „Bekannt“'
		} as Record<string, string>
	},

	event: {
		back: 'Zu den Aufträgen',
		traveling: 'Unterwegs',
		arrived: 'Angekommen.',
		chance: (n: number) => `${n} %`,
		combat: 'Kampf',
		combatNote: 'Kämpfe kommen mit dem Duellsystem. Bis dahin gehen sie verloren.',
		check: (roll: number, total: number, difficulty: number) =>
			`W20: ${roll} → ${total} gegen ${difficulty}`,
		success: 'Gelungen',
		failure: 'Misslungen',
		result: 'Ergebnis',
		blocked: {
			requires_item: 'Dir fehlt etwas',
			requires_dollars: 'Zu wenig Geld',
			requires_class: 'Nicht deine Klasse',
			requires_reputation: 'Ruf zu niedrig',
			requires_corruption: 'Nicht für dich'
		} as Record<string, string>,
		applied: {
			xp: (n: number) => `+${n} XP`,
			level: (n: number) => (n === 1 ? 'Neue Stufe!' : `${n} neue Stufen!`),
			corruption: (n: number) => `Verderbnis ${n > 0 ? '+' : ''}${n}`,
			item: (name: string) => `Erhalten: ${name}`,
			unlock: 'Etwas Neues ist freigeschaltet.',
			built: (name: string, level: number) => `${name} Stufe ${level}`,
			delay: (n: number) => `${n} min aufgehalten`,
			combat: 'Kampf verloren',
			stored: 'Die Folgen zeigen sich später.'
		}
	},

	items: {
		strange_coat: 'Fremder Mantel',
		bell_shard: 'Glockensplitter'
	} as Record<string, string>,

	errors: {
		not_authenticated: 'Bitte melde dich an.',
		invalid_credentials: 'Benutzername oder Passwort stimmt nicht.',
		username_taken: 'Dieser Benutzername ist schon vergeben.',
		username_length: 'Der Benutzername muss 3 bis 20 Zeichen lang sein.',
		username_chars: 'Erlaubt sind Buchstaben ohne Umlaute, Ziffern, _ und -.',
		password_length: 'Das Passwort muss mindestens 8 Zeichen lang sein.',
		invalid_password: 'Das Passwort stimmt nicht.',
		unknown_building: 'Dieses Gebäude gibt es nicht.',
		main_house_too_low: 'Dafür muss zuerst das Haupthaus höher sein.',
		not_enough_resources: 'Dafür reichen deine Vorräte nicht.',
		queue_full: 'Alle Bauplätze sind belegt.',
		already_building: 'Daran wird schon gebaut.',
		excluded: 'Das verträgt sich nicht mit einem anderen Gebäude.',
		max_level: 'Das Gebäude hat die höchste Stufe.',
		not_found: 'Das gibt es nicht mehr.',
		unknown_job: 'Diese Arbeit gibt es nicht.',
		job_running: 'Du arbeitest schon.',
		no_job_running: 'Du arbeitest gerade nicht.',
		no_character: 'Leg zuerst einen Charakter an.',
		nothing_to_spend: 'Du hast nichts verteilt.',
		not_enough_attribute_points: 'So viele Attributpunkte hast du nicht.',
		not_enough_skill_points: 'So viele Skillpunkte hast du nicht.',
		skill_cap: 'Ein Skill darf höchstens Stufe + 2 Punkte haben.',
		unknown_skill: 'Unbekannter Skill.',
		busy: 'Du bist gerade mit etwas anderem beschäftigt.',
		unknown_quest: 'Diesen Auftrag gibt es nicht.',
		not_available: 'Dieser Auftrag ist gerade nicht verfügbar.',
		wrong_region: 'Dafür musst du erst dorthin reisen.',
		done_today: 'Heute schon erledigt.',
		in_progress: 'Der Auftrag läuft schon.',
		reputation_too_low: 'Dein Ruf reicht dafür nicht.',
		no_choice_pending: 'Hier ist schon entschieden.',
		unknown_option: 'Diese Möglichkeit gibt es nicht.',
		requires_item: 'Dir fehlt etwas dafür.',
		requires_dollars: 'Dafür fehlt dir Geld.',
		requires_class: 'Das kann nur eine andere Klasse.',
		requires_reputation: 'Dein Ruf reicht dafür nicht.',
		requires_corruption: 'Das steht dir nicht offen.',
		unknown_region: 'Diesen Ort gibt es nicht.',
		already_there: 'Da bist du schon.',
		gorge_closed: 'Die Schlucht lässt dich erst ab Hüter „Bekannt“ durch.',
		no_oath_faction: 'Schwören kann man nur der Kompanie oder der Aschenbande.',
		already_sworn: 'Du hast schon geschworen.',
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
