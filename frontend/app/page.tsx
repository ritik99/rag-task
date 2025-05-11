"use client";

import { useState, FormEvent } from "react"; // Removed useEffect
import { Source, RagQueryResponse, MetricScore } from "@/lib/types"; // Updated types
import { cn } from "@/lib/utils";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Loader2 } from "lucide-react";

const FASTAPI_BACKEND_URL = process.env.NEXT_PUBLIC_FASTAPI_BACKEND_URL || "http://localhost:8000";

export default function Home() {
  const [inputValue, setInputValue] = useState("");
  const [llmAnswer, setLlmAnswer] = useState("");
  const [chatError, setChatError] = useState<Error | null>(null);

  const [referenceAnswer, setReferenceAnswer] = useState("");
  const [ragSources, setRagSources] = useState<Source[]>([]);
  const [evaluationScores, setEvaluationScores] = useState<MetricScore | null>(null); // Changed from evaluationResults
  
  const [isLoading, setIsLoading] = useState(false); // Combined loading state
  const [showEvaluationPanel, setShowEvaluationPanel] = useState(false);

  const handleFullSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setRagSources([]);
    setLlmAnswer("");
    setChatError(null);
    setEvaluationScores(null); // Clear previous scores
    
    const hasReference = referenceAnswer.trim() !== "";
    setShowEvaluationPanel(hasReference); // Show panel if reference answer exists

    if (!inputValue.trim()) {
      setChatError(new Error("Query cannot be empty."));
      if (hasReference) setShowEvaluationPanel(true); // Keep panel visible if reference was there
      else setShowEvaluationPanel(false);
      return;
    }

    setIsLoading(true);
    try {
      const requestBody: any = { query: inputValue, top_k: 3 };
      if (hasReference) {
        requestBody.reference_answer = referenceAnswer;
      }

      const ragApiResponse = await fetch(`${FASTAPI_BACKEND_URL}/api/v1/rag/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!ragApiResponse.ok) {
        const errorData = await ragApiResponse.json();
        throw new Error(errorData.detail || "Failed to fetch RAG response");
      }
      const responseData: RagQueryResponse = await ragApiResponse.json();
      setLlmAnswer(responseData.answer);
      setRagSources(responseData.sources || []);
      
      if (responseData.evaluation_scores) {
        console.log(`[handleFullSubmit] Evaluation scores are ${JSON.stringify(responseData.evaluation_scores)}`)
        setEvaluationScores(responseData.evaluation_scores);
      } else if (hasReference) {
        // If reference was provided but no scores, it might be an issue or all scores were null
        console.warn("Reference answer provided, but no evaluation scores received from backend.");
        setEvaluationScores({}); // Set to empty object to indicate attempt but no data
      }

    } catch (err) {
      console.error("RAG query/evaluation error:", err);
      setChatError(err instanceof Error ? err : new Error("An unknown error occurred."));
      setLlmAnswer("Failed to get an answer. Please try again.");
      if (hasReference) setEvaluationScores({}); // Show panel with N/A if error
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreDisplay = (metricKey: keyof MetricScore): string => { // Use keyof MetricScore
    if (!evaluationScores) return "N/A";
    // Check if evaluationScores is an empty object (error or no scores case)
    if (Object.keys(evaluationScores).length === 0 && evaluationScores.constructor === Object) return "N/A";

    const scoreValue = evaluationScores[metricKey];
    if (scoreValue !== undefined && scoreValue !== null) {
      return (scoreValue).toFixed(3);
    }
    return "N/A";
  };
  
  const metricDisplayConfig = [
    { key: "response_relevancy" as keyof MetricScore, displayName: "Response Relevancy (LLM)", color: "text-blue-400" },
    { key: "rouge_score" as keyof MetricScore, displayName: "Rouge Score (non-LLM)", color: "text-yellow-400" },
    { key: "bleu_score" as keyof MetricScore, displayName: "Bleu Score (non-LLM)", color: "text-green-400"},
  ];


  return (
    <div className="min-h-screen bg-black text-foreground">
      <div className="max-w-[1000px] mx-auto px-8 md:px-16 py-8">
        <header className="mb-6">
          <h1 className="text-center">
            RAG TESTING
          </h1>
        </header>

        {chatError && (
          <Card className="w-full mb-6 bg-destructive/10 border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">Chat Error</CardTitle>
            </CardHeader>
            <CardContent>
              <p>{chatError.message}</p>
            </CardContent>
          </Card>
        )}

        <div className={cn(
          "grid gap-4", 
          showEvaluationPanel ? "md:grid-cols-[2fr_1fr]" : "grid-cols-1" 
        )}>
        <div> {/* Left column */}
          <Card className="bg-black/40">
            <CardHeader className="border-b border-muted-foreground/20">
              <CardTitle><h2>QUERY</h2></CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleFullSubmit} className="space-y-4">
                <div>
                  <Label htmlFor="query-input" className="sr-only">Query</Label>
                  <Textarea
                    id="query-input"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Enter your query..."
                    className="min-h-[100px] text-foreground" 
                    disabled={isLoading}
                  />
                </div>
                <div>
                  <Label htmlFor="reference-answer-input" className="sr-only">Optional Reference Answer</Label>
                  <Textarea
                    id="reference-answer-input"
                    value={referenceAnswer}
                    onChange={(e) => setReferenceAnswer(e.target.value)}
                    placeholder="Optional Reference Answer"
                    className="min-h-[80px] text-foreground" 
                    disabled={isLoading}
                  />
                </div>
                <Button
                  type="submit"
                  disabled={isLoading || !inputValue.trim()}
                  className="w-full text-base"
                >
                  {isLoading && <Loader2 className="mr-2 h-5 w-5 animate-spin" />}
                  {isLoading ? (referenceAnswer.trim() ? "Processing & Evaluating..." : "Getting Answer...") : "Submit Query"}
                </Button>
              </form>
            </CardContent>
          </Card>

          <Card className="bg-black/40">
            <CardHeader className="border-b border-muted-foreground/20">
              <CardTitle><h2>OUTPUT</h2></CardTitle>
            </CardHeader>
            <CardContent className="min-h-[150px] text-base bg-black/70 border border-muted-foreground/30 p-4 rounded-md">
              {isLoading && (
                <div className="flex items-center text-muted-foreground">
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  <span>{referenceAnswer.trim() ? "Processing & Evaluating..." : "Loading answer..."}</span>
                </div>
              )}
              {!isLoading && llmAnswer && (
                <div className="whitespace-pre-wrap">{llmAnswer}</div>
              )}
              {!isLoading && !llmAnswer && !chatError && (
                <p className="text-muted-foreground">LLM Answer will appear here...</p>
              )}
               {!isLoading && !llmAnswer && chatError && (
                <p className="text-destructive">{chatError.message.includes("Query cannot be empty") ? chatError.message : "Failed to load answer."}</p>
              )}
            </CardContent>
          </Card>

          <Card className="bg-black/40">
            <CardHeader className="border-b border-muted-foreground/20">
              <CardTitle><h2>SOURCES</h2></CardTitle>
            </CardHeader>
            <CardContent className="min-h-[100px] text-sm">
              {ragSources.length > 0 ? (
                <ul className="space-y-4">
                  {ragSources.map((source, index) => (
                    <li key={source.id || `source-${index}`} className="p-4 bg-black/70 rounded-md border border-muted-foreground/30 relative">
                      <div className="flex items-start">
                        <div className="flex-1">
                          <p className="font-semibold text-foreground">{source.document_name || "Unknown Document"}</p>
                          <p className="text-muted-foreground mt-2 break-words">"{source.snippet}"</p>
                          {/*{source.score !== undefined && <p className="text-xs text-muted-foreground/70 mt-2">Score: {source.score.toFixed(3)}</p>}*/}
                        </div>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                 <p className="text-muted-foreground">
                  {isLoading ? "Loading sources..." : "Sources used for RAG will appear here..."}
                </p>
              )}
            </CardContent>
          </Card>
        </div>

        {showEvaluationPanel && (
          <div className="sticky top-8 h-fit">
            <Card className="bg-black/40">
              <CardHeader className="border-b border-muted-foreground/20">
                <CardTitle><h2>SCORE</h2></CardTitle>
              </CardHeader>
              <CardContent>
                {isLoading && referenceAnswer.trim() && (
                  <div className="flex flex-col justify-center items-center py-10">
                    <Loader2 className="h-12 w-12 animate-spin text-primary mb-3" />
                    <p className="text-muted-foreground">Calculating scores...</p>
                  </div>
                )}

                {!isLoading && chatError && referenceAnswer.trim() && (
                  <div className="text-center py-10 text-destructive">
                    <p className="font-semibold">Evaluation Note</p>
                    <p className="text-sm">Scores could not be calculated due to an error.</p>
                  </div>
                )}
                
                {!isLoading && !chatError && evaluationScores && (
                  <div className="flex flex-row justify-around items-center py-6">
                    {metricDisplayConfig.map(metric => (
                       <div className="text-center" key={metric.key}>
                         <p className={cn("text-6xl md:text-7xl font-bold", metric.color)}>{getScoreDisplay(metric.key)}</p>
                         <h4>{metric.displayName}</h4>
                       </div>
                    ))}
                     {Object.keys(evaluationScores).length === 0 && evaluationScores.constructor === Object && !chatError && (
                        <p className="text-muted-foreground text-center py-10">Evaluation attempted, but no scores were returned. Check backend logs.</p>
                     )}
                  </div>
                )}

                {!isLoading && !evaluationScores && referenceAnswer.trim() && !chatError && (
                   <p className="text-muted-foreground text-center py-10">Scores will appear here after processing.</p>
                )}
                 {!isLoading && !referenceAnswer.trim() && (
                  <p className="text-muted-foreground text-center py-10">Provide a reference answer to see scores.</p>
                )}
              </CardContent>
            </Card>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
