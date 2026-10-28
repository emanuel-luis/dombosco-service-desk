import { afterEach, describe, expect, it, vi } from "vitest";
import { buildUrl, request } from "./client";
import { ApiError } from "./errors";

describe("buildUrl", () => {
  it("joins base, api prefix and path", () => {
    expect(buildUrl("/forms/parent/", {}, "http://api.test")).toBe(
      "http://api.test/api/v1/forms/parent/",
    );
  });

  it("adds the query and skips undefined values", () => {
    expect(
      buildUrl("/forms/parent/", { id: 7, status: undefined }, "http://api.test"),
    ).toBe("http://api.test/api/v1/forms/parent/?id=7");
  });

  it("encodes query values", () => {
    expect(
      buildUrl("/forms/parent/", { assigned_staff: "a+b@x.com" }, ""),
    ).toBe("/api/v1/forms/parent/?assigned_staff=a%2Bb%40x.com");
  });
});

describe("request", () => {
  afterEach(() => vi.unstubAllGlobals());

  const reply = (status: number, body = "") =>
    vi.fn().mockResolvedValue(new Response(body, { status }));

  it("returns the parsed JSON body", async () => {
    vi.stubGlobal("fetch", reply(200, '{"ok":true}'));
    await expect(request("GET", "/auth/user/", { auth: false })).resolves.toEqual({
      ok: true,
    });
  });

  it("throws an ApiError with the pt-BR message", async () => {
    vi.stubGlobal("fetch", reply(409));
    await expect(request("PUT", "/x/", { auth: false })).rejects.toMatchObject({
      status: 409,
      message: expect.stringContaining("estado atual"),
    });
  });

  it("prefers a per-call message", async () => {
    vi.stubGlobal("fetch", reply(400));
    await expect(
      request("POST", "/x/", { auth: false, messages: { 400: "Ruim." } }),
    ).rejects.toThrow("Ruim.");
  });

  it("reports an unreachable server as status 0", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("fail")));
    const error = (await request("GET", "/x/", { auth: false }).catch((e) => e)) as ApiError;
    expect(error).toBeInstanceOf(ApiError);
    expect(error.status).toBe(0);
  });
});
