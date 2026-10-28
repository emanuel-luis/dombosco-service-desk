// Students are minors: accept a real calendar date that is not in the future
// and gives a plausible school age.
const MIN_AGE = 2;
const MAX_AGE = 25;

// Parses DD/MM/YYYY; returns null when it is not a real calendar date.
export function parseBrDate(value: string): Date | null {
  const match = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(value);
  if (!match) return null;
  const day = Number(match[1]);
  const month = Number(match[2]);
  const year = Number(match[3]);
  const date = new Date(year, month - 1, day);
  const real =
    date.getFullYear() === year &&
    date.getMonth() === month - 1 &&
    date.getDate() === day;
  return real ? date : null;
}

export function isPlausibleBirthDate(
  value: string,
  today = new Date(),
): boolean {
  const date = parseBrDate(value);
  if (!date || date > today) return false;
  let age = today.getFullYear() - date.getFullYear();
  const beforeBirthday =
    today.getMonth() < date.getMonth() ||
    (today.getMonth() === date.getMonth() && today.getDate() < date.getDate());
  if (beforeBirthday) age -= 1;
  return age >= MIN_AGE && age <= MAX_AGE;
}

export const toIsoDate = (value: string) => value.split("/").reverse().join("-");
