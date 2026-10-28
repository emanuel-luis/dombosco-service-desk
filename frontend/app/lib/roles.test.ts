import { describe, expect, it } from "vitest";
import {
  allowedStatuses,
  canAnswer,
  canCreateRequest,
  canEditComment,
  canEditOrDelete,
  parseRole,
} from "./roles";
import { FormStatus, ParentForm, UserInfo } from "./types";

const user: UserInfo = {
  pk: 1,
  email: "ana@example.com",
  first_name: "Ana",
  last_name: "Souza",
  groups: [],
  role: "parent",
};

const form = (status: FormStatus, email = "ana@example.com") =>
  ({ id: 1, status, responsible_party: { email } }) as ParentForm;

describe("parseRole", () => {
  it("keeps the roles the API defines", () => {
    for (const role of ["admin", "staff", "parent", "user", "visitor"]) {
      expect(parseRole(role)).toBe(role);
    }
  });

  it("falls back to visitor for anything else", () => {
    expect(parseRole("root")).toBe("visitor");
    expect(parseRole(undefined)).toBe("visitor");
    expect(parseRole(2)).toBe("visitor");
  });
});

describe("request actions", () => {
  it("only parents create requests", () => {
    expect(canCreateRequest("parent")).toBe(true);
    expect(canCreateRequest("staff")).toBe(false);
    expect(canCreateRequest("admin")).toBe(false);
  });

  it("parents edit or delete only their own pending requests", () => {
    expect(canEditOrDelete("parent", form(0), user)).toBe(true);
    expect(canEditOrDelete("parent", form(1), user)).toBe(false);
    expect(canEditOrDelete("parent", form(0, "other@example.com"), user)).toBe(false);
    expect(canEditOrDelete("staff", form(0), user)).toBe(false);
  });

  it("staff answer pending requests only", () => {
    expect(canAnswer("staff", form(0))).toBe(true);
    expect(canAnswer("staff", form(1))).toBe(false);
    expect(canAnswer("parent", form(0))).toBe(false);
  });
});

describe("allowedStatuses", () => {
  it("lets staff finalize or cancel assigned requests in progress", () => {
    expect(allowedStatuses("staff", 1, true)).toEqual([2, 3]);
  });

  it("gives staff nothing on unassigned or non-active requests", () => {
    expect(allowedStatuses("staff", 1, false)).toEqual([]);
    expect(allowedStatuses("staff", 0, true)).toEqual([]);
    expect(allowedStatuses("staff", 2, true)).toEqual([]);
  });

  it("lets admins pick any other status", () => {
    expect(allowedStatuses("admin", 2, false)).toEqual([0, 1, 3]);
  });

  it("gives parents nothing", () => {
    expect(allowedStatuses("parent", 1, true)).toEqual([]);
  });
});

describe("canEditComment", () => {
  it("allows the author, matched by user id, while in progress", () => {
    expect(canEditComment(1, 1, user)).toBe(true);
  });

  it("blocks other authors and other statuses", () => {
    expect(canEditComment(2, 1, user)).toBe(false);
    expect(canEditComment(1, 2, user)).toBe(false);
    expect(canEditComment(1, 1, null)).toBe(false);
  });
});
