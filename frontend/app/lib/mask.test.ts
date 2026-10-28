import { describe, expect, it } from "vitest";
import { applyMask } from "./mask";

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
