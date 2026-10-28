// Digit mask: "9" is a digit slot, anything else is a literal ("(99) 99999-9999").
export function applyMask(value: string, mask: string): string {
  const digits = value.replace(/\D/g, "");
  let out = "";
  let i = 0;
  for (const ch of mask) {
    if (i >= digits.length) break;
    if (ch === "9") out += digits[i++];
    else out += ch;
  }
  return out;
}

// Number of digits in `value` before caret position `pos`.
export function digitsBefore(value: string, pos: number): number {
  return value.slice(0, pos).replace(/\D/g, "").length;
}

// Caret position right after the n-th digit of `formatted`. With `skipLiterals`,
// also moves past the separators that follow it (typing forward).
export function caretAfterDigits(formatted: string, n: number, skipLiterals = true): number {
  let seen = 0;
  let pos = 0;
  if (n > 0) {
    for (; pos < formatted.length; pos++) {
      if (/\d/.test(formatted[pos]) && ++seen === n) {
        pos++;
        break;
      }
    }
  }
  if (skipLiterals) while (pos < formatted.length && /\D/.test(formatted[pos])) pos++;
  return pos;
}

// Number of digit slots in a mask ("99/99/9999" -> 8).
export function maskSlots(mask: string): number {
  return mask.split("").filter((ch) => ch === "9").length;
}

// True when an edit would push a digit out of a field that was already full.
export function overflowsFullMask(previous: string, next: string, mask: string): boolean {
  const slots = maskSlots(mask);
  const count = (s: string) => s.replace(/\D/g, "").length;
  return count(previous) >= slots && count(next) > slots;
}
