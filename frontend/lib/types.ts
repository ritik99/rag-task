export interface Source {
  id: string;
  document_name: string;
  snippet: string;
  score?: number;
}

export interface MetricScore {
  response_relevancy?: number | null;
  bleu_score?: number | null;
  rouge_score?: number | null;
}

export interface RagQueryResponse {
  answer: string;
  sources: Source[];
  query_time_ms?: number;
  evaluation_scores?: MetricScore;
}

export interface ChatRequestBody {
  messages: { role: "user" | "assistant" | "system"; content: string }[];
}
