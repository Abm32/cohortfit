import type {
  ApiError,
  AuditReport,
  Protocol,
  ProtocolCard,
  ProvenanceResponse,
} from "../types/audit";

const API_BASE = import.meta.env.DEV ? "/api" : "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { Accept: "application/json", ...init?.headers },
    ...init,
  });
  if (!res.ok) {
    const body = (await res.json().catch(() => ({}))) as ApiError;
    const detail =
      typeof body.detail === "string"
        ? body.detail
        : JSON.stringify(body.detail ?? res.statusText);
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export function fetchSampleReport(): Promise<AuditReport> {
  return request<AuditReport>("/fixtures/reports/sample");
}

export function fetchPartialCoverageReport(): Promise<AuditReport> {
  return request<AuditReport>("/fixtures/reports/partial-coverage");
}

export function fetchProtocolCatalogue(): Promise<ProtocolCard[]> {
  return request<ProtocolCard[]>("/fixtures/protocols");
}

export function fetchProtocolBySlug(slug: string): Promise<Protocol> {
  return request<Protocol>(`/fixtures/protocols/${slug}`);
}

export function fetchDemoProtocol(): Promise<Protocol> {
  return request<Protocol>("/fixtures/protocols/demo");
}

export function auditProtocol(protocol: Protocol, offline = true): Promise<AuditReport> {
  return request<AuditReport>(`/audit?offline=${offline}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(protocol),
  });
}

export function fetchProvenance(gene: string): Promise<ProvenanceResponse> {
  return request<ProvenanceResponse>(`/provenance/${encodeURIComponent(gene)}`);
}

export function extractProtocol(prose: string): Promise<Protocol> {
  return request<Protocol>("/extract", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prose }),
  });
}

export function isExtractUnavailableError(message: string): boolean {
  return message.startsWith("503:");
}
