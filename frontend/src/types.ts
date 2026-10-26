export type RetrievedChunk = {
  document_id: string;
  document_title: string;
  chunk_index: number;
  text: string;
  distance: number;
  match: string;
  cite_n: number;
  cited: boolean | null;
};

export type StreamEvent =
  | { type: "sources"; sources: RetrievedChunk[] }
  | { type: "token"; text: string }
  | { type: "done"; answer: string }
  | { type: "error"; detail: string };

export type ChatTurn = {
  role: "user" | "assistant";
  content: string;
};
