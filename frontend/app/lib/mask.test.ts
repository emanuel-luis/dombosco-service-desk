import { describe, expect, it } from "vitest";
import {
  applyMask,
  caretAfterDigits,
  digitsBefore,
  maskSlots,
  overflowsFullMask,
} from "./mask";

describe("applyMask", () => {
  it("formats a phone number", () => {
    expect(applyMask("98999887766", "(99) 99999-9999")).toBe("(98) 99988-7766");
    expect(applyMask("(98) 9", "(99) 99999-9999")).toBe("(98) 9");
  });
  it("formats a date and ignores non-digits and overflow", () => {
    expect(applyMask("0102", "99/99/9999")).toBe("01/02");
    expect(applyMask("01/02/2000x99", "99/99/9999")).toBe("01/02/2000");
    expect(applyMask("", "99/99/9999")).toBe("");
  });
});

describe("digitsBefore", () => {
  it("counts digits before the caret, ignoring separators", () => {
    expect(digitsBefore("01/02/2000", 0)).toBe(0);
    expect(digitsBefore("01/02/2000", 3)).toBe(2);
    expect(digitsBefore("(98) 99988", 5)).toBe(2);
    expect(digitsBefore("01/02", 99)).toBe(4);
  });
});

describe("caretAfterDigits", () => {
  it("returns the position after the n-th digit, skipping following separators", () => {
    expect(caretAfterDigits("01/02/2000", 2)).toBe(3);
    expect(caretAfterDigits("01/02/2000", 2, false)).toBe(2);
    expect(caretAfterDigits("(98) 99988", 2)).toBe(5);
    expect(caretAfterDigits("(98) 99988", 1, false)).toBe(2);
  });
  it("handles boundaries", () => {
    expect(caretAfterDigits("01/02", 0, false)).toBe(0);
    expect(caretAfterDigits("(98", 0)).toBe(1);
    expect(caretAfterDigits("01/02", 4)).toBe(5);
    expect(caretAfterDigits("01/02", 9)).toBe(5);
    expect(caretAfterDigits("", 3)).toBe(0);
  });
  it("round-trips with applyMask for a mid-field insert", () => {
    const raw = "1x2/34"; // user typed x... digits before caret(2) = 1
    const n = digitsBefore(raw, 2);
    expect(caretAfterDigits(applyMask(raw, "99/99/9999"), n, false)).toBe(1);
  });
});

describe("overflowsFullMask", () => {
  it("counts the digit slots of a mask", () => {
    expect(maskSlots("99/99/9999")).toBe(8);
    expect(maskSlots("(99) 99999-9999")).toBe(11);
  });
  it("flags only an insert into a field that was already full", () => {
    expect(overflowsFullMask("01/02/2000", "01/092/2000", "99/99/9999")).toBe(true);
    expect(overflowsFullMask("01/02/200", "01/02/2000", "99/99/9999")).toBe(false);
    expect(overflowsFullMask("", "123456789", "99/99/9999")).toBe(false);
    expect(overflowsFullMask("01/02/2000", "01/0/2000", "99/99/9999")).toBe(false);
  });
});
