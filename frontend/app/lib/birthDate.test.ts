import { describe, expect, it } from "vitest";
import { isPlausibleBirthDate, parseBrDate, toIsoDate } from "./birthDate";

const today = new Date(2026, 9, 27);

describe("isPlausibleBirthDate", () => {
  it("accepts a minor of school age", () => {
    expect(isPlausibleBirthDate("15/03/2014", today)).toBe(true);
  });

  it("rejects future dates and impossible dates", () => {
    expect(isPlausibleBirthDate("01/01/2030", today)).toBe(false);
    expect(isPlausibleBirthDate("31/02/2014", today)).toBe(false);
    expect(isPlausibleBirthDate("2014-03-15", today)).toBe(false);
  });

  it("rejects ages outside the school range", () => {
    expect(isPlausibleBirthDate("01/01/2026", today)).toBe(false);
    expect(isPlausibleBirthDate("01/01/1980", today)).toBe(false);
  });
});

describe("date helpers", () => {
  it("parses DD/MM/YYYY and converts to ISO", () => {
    expect(parseBrDate("15/03/2014")?.getMonth()).toBe(2);
    expect(parseBrDate("99/99/9999")).toBeNull();
    expect(toIsoDate("15/03/2014")).toBe("2014-03-15");
  });
});
