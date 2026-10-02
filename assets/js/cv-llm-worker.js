/*
 * =========================================================
 * ARAD CV — WEBLLM WORKER
 * =========================================================
 *
 * IMPORTANT:
 * WebLLM is intentionally pinned to 0.2.82.
 *
 * Versions 0.2.83+ have a reported WebGPU prefill
 * regression that can produce:
 *
 * "Object has already been disposed"
 *
 * with longer RAG prompts.
 * =========================================================
 */

import {
  WebWorkerMLCEngineHandler
} from "https://esm.run/@mlc-ai/web-llm@0.2.82";


const handler =
  new WebWorkerMLCEngineHandler();


self.onmessage = (
  event
) => {
  handler.onmessage(
    event
  );
};