const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// TODO: Replace `any` with real typed interfaces from lib/types.ts
export async function postAssessment(data: any) {
  const res = await fetch(`${API_BASE}/api/assessment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function postCredit(data: any) {
  const res = await fetch(`${API_BASE}/api/credit/assess`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  return res.json();
}

export async function postPlan(sessionId: string) {
  const res = await fetch(`${API_BASE}/api/plan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ session_id: sessionId }),
  });
  return res.json();
}
