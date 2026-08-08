import { describe, expect, it } from "vitest";
import {
  formatCitationList,
  formatExpectedN,
  formatFraction,
  pubmedUrl,
  tierLabel,
  tierSubtitle,
} from "./display";

/** Golden vectors — must match tests/test_display.py */

describe("formatFraction", () => {
  it("zero", () => expect(formatFraction(0)).toBe("0%"));
  it("poor metabolizer rare", () => expect(formatFraction(0.000194)).toBe("0.02%"));
  it("intermediate", () => expect(formatFraction(0.0452)).toBe("4.5%"));
  it("normal", () => expect(formatFraction(0.9546)).toBe("95.5%"));
});

describe("formatExpectedN", () => {
  it("zero", () => expect(formatExpectedN(0)).toBe("0"));
  it("poor metabolizer small", () => expect(formatExpectedN(0.04)).toBe("0.04"));
  it("intermediate", () => expect(formatExpectedN(10.4)).toBe("10.4"));
});

describe("tier meta", () => {
  it("tier0", () => {
    expect(tierLabel(0)).toBe("TIER 0");
    expect(tierSubtitle(0)).toContain("HWE");
  });
  it("tier1", () => expect(tierLabel(1)).toBe("TIER 1"));
  it("tier2", () => expect(tierLabel(2)).toBe("SCENARIO"));
});

describe("citations", () => {
  it("pubmed url", () =>
    expect(pubmedUrl("29152729")).toBe("https://pubmed.ncbi.nlm.nih.gov/29152729/"));
  it("tier1 missing", () =>
    expect(formatCitationList([], true)).toContain("MISSING"));
});
