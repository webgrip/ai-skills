const en = {
  loading: "Loading service status",
  states: { healthy: "Healthy", degraded: "Degraded", down: "Down" },
  release: "Release",
  replicas: "Replicas ready",
  updated: "Updated",
  restart: "Restart",
  confirmRestart: "Confirm restart",
  cancel: "Cancel",
  restartRequested: "Restart requested",
  restartAccepted: "Restart accepted",
  restartNotAllowed: "You cannot restart this service from here.",
  actionsUnavailable: "Ask in the chat to change this service.",
  unreadable: "This result could not be shown. The text answer above has the details.",
  failed: "That did not work",
} as const;

type Messages = { [K in keyof typeof en]: (typeof en)[K] extends string ? string : { [S in keyof (typeof en)[K]]: string } };

const de: Messages = {
  loading: "Dienststatus wird geladen",
  states: { healthy: "Fehlerfrei", degraded: "Beeinträchtigt", down: "Ausgefallen" },
  release: "Version",
  replicas: "Bereite Replikate",
  updated: "Aktualisiert",
  restart: "Neu starten",
  confirmRestart: "Neustart bestätigen",
  cancel: "Abbrechen",
  restartRequested: "Neustart angefordert",
  restartAccepted: "Neustart angenommen",
  restartNotAllowed: "Sie können diesen Dienst hier nicht neu starten.",
  actionsUnavailable: "Bitten Sie im Chat darum, diesen Dienst zu ändern.",
  unreadable: "Dieses Ergebnis kann nicht angezeigt werden. Die Textantwort oben enthält die Details.",
  failed: "Das hat nicht funktioniert",
};

const catalogs: Record<string, Messages> = { en, de };

export interface Locale {
  tag: string;
  messages: Messages;
  formatDateTime: (iso: string) => string;
}

function supportedTag(requested: string | undefined): string | undefined {
  try {
    return requested ? Intl.DateTimeFormat.supportedLocalesOf([requested])[0] : undefined;
  } catch {
    return undefined;
  }
}

function dateTimeFormatter(tag: string, timeZone: string | undefined): Intl.DateTimeFormat {
  try {
    return new Intl.DateTimeFormat(tag, { dateStyle: "medium", timeStyle: "short", timeZone: timeZone ?? "UTC" });
  } catch {
    return new Intl.DateTimeFormat(tag, { dateStyle: "medium", timeStyle: "short", timeZone: "UTC" });
  }
}

export function resolveLocale(requested: string | undefined, timeZone: string | undefined): Locale {
  const candidate = supportedTag(requested);
  const language = candidate?.split("-")[0].toLowerCase();
  const tag = candidate && language && catalogs[language] ? candidate : "en";
  const formatter = dateTimeFormatter(tag, timeZone);
  return {
    tag,
    messages: catalogs[tag.split("-")[0].toLowerCase()] ?? en,
    formatDateTime: (iso) => formatter.format(new Date(iso)),
  };
}
