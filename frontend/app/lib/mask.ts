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
