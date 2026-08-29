export interface ChatMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  relevance_score?: number | null;
  is_crisis?: boolean;
  created_at?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  message_count: number;
  crisis_flagged: boolean;
  started_at: string;
}

export interface ChatResponse {
  response: string;
  is_crisis: boolean;
  is_relevant: boolean;
  relevance_score: number;
  few_shot_count: number;
  session_id: string;
}
