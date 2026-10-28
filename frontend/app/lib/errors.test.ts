import { describe, expect, it } from "vitest";
import { ApiError, messageForStatus, NETWORK_MESSAGE, toMessage } from "./errors";

describe("messageForStatus", () => {
  it("maps each documented status to a pt-BR message", () => {
    for (const status of [400, 401, 403, 404, 409]) {
      expect(messageForStatus(status)).toMatch(/[a-zç]{3,}/i);
    }
    expect(messageForStatus(403)).toBe(
      "Você não tem permissão para realizar esta ação.",
    );
    expect(messageForStatus(409)).toContain("estado atual");
  });

  it("covers 5xx and unreachable servers", () => {
    expect(messageForStatus(500)).toBe(messageForStatus(503));
    expect(messageForStatus(500)).toContain("servidor");
    expect(messageForStatus(0)).toBe(NETWORK_MESSAGE);
  });

  it("uses a generic message for other statuses", () => {
    expect(messageForStatus(418)).toBe(toMessage(new Error("x")));
  });
});

describe("toMessage", () => {
  it("shows the ApiError message and hides unknown errors", () => {
    expect(toMessage(new ApiError(404))).toBe(messageForStatus(404));
    expect(toMessage(new ApiError(400, "Custom"))).toBe("Custom");
    expect(toMessage("boom")).not.toContain("boom");
  });
});
