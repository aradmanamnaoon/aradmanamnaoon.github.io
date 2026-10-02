/*
=========================================================
ARAD CV CHAT ENGINE
=========================================================

Local AI CV assistant.

Architecture:

User Question
      |
      v
cv-rag.js
      |
      v
Semantic Retrieval
      |
      v
Evidence Selection
      |
      v
WebLLM
      |
      v
Grounded Answer


No API key.
No backend.
GitHub Pages compatible.

=========================================================
*/


import {
  initializeCvRag,
  retrieveCvContext
} from "./cv-rag.js";



const CONFIG = {

  model:
    "Qwen2.5-0.5B-Instruct-q4f32_1-MLC",


  webllm:
    "https://esm.run/@mlc-ai/web-llm@0.2.82",


  maxSources:
    3,


  maxTokens:
    220,


  temperature:
    0,


  topP:
    0.9,


  minimumScore:
    0.28

};





let engine = null;

let enginePromise = null;

let webllmPromise = null;





const UNKNOWN =
"That information is not available in Arad's provided CV/portfolio context.";






const SYSTEM_PROMPT = `

You are Arad's CV portfolio assistant.

Answer questions ONLY using the provided verified evidence.

Rules:

- If evidence exists, answer the question.
- Never say information is unavailable when evidence exists.
- Start with the most relevant project or experience.
- Explain what Arad built or implemented.
- Mention technologies when available.
- Mention metrics only when provided.
- Do not invent employers.
- Do not invent education.
- Do not invent personal information.
- Do not claim clinical validation unless explicitly stated.
- Use citations like [1], [2].

If the evidence does not contain the answer, reply exactly:

"${UNKNOWN}"

`;





function progress(callback, data) {

  if (
    typeof callback === "function"
  ) {

    callback(data);

  }

}
/*
=========================================================
WEBGPU SUPPORT
=========================================================
*/


export async function checkCvChatSupport() {

  const result = {

    webgpu:
      false,


    supported:
      false,


    reason:
      null

  };



  if (
    !navigator.gpu
  ) {

    result.reason =
      "WebGPU is not available in this browser.";

    return result;

  }



  try {

    const adapter =
      await navigator.gpu.requestAdapter();



    if (!adapter) {

      result.reason =
        "No compatible GPU adapter found.";

      return result;

    }



    result.webgpu =
      true;


    result.supported =
      true;


  }

  catch(error) {


    result.reason =
      error.message;


  }



  return result;

}








/*
=========================================================
LOAD WEBLLM MODULE
=========================================================
*/


async function loadWebLLM() {


  if (
    !webllmPromise
  ) {


    webllmPromise =
      import(
        CONFIG.webllm
      );


  }



  return webllmPromise;


}








/*
=========================================================
INITIALIZE CHAT MODEL

Important:

Nothing downloads until this function
is called.

=========================================================
*/


export async function initializeCvChat(
  callback = null
) {


  if (
    engine
  ) {

    return engine;

  }



  if (
    enginePromise
  ) {

    return enginePromise;

  }







  enginePromise =
    (async()=>{


      progress(
        callback,
        {

          stage:
            "checking-browser",


          message:
            "Checking WebGPU support..."

        }
      );






      const support =
        await checkCvChatSupport();






      if (
        !support.supported
      ) {

        throw new Error(
          support.reason
        );

      }







      progress(
        callback,
        {

          stage:
            "loading-rag",


          message:
            "Loading CV knowledge base..."

        }
      );






      await initializeCvRag();








      progress(
        callback,
        {

          stage:
            "loading-model",


          message:
            "Loading local AI model..."

        }
      );








      const {

        CreateMLCEngine

      } =
        await loadWebLLM();









      engine =
        await CreateMLCEngine(

          CONFIG.model,


          {


            initProgressCallback:
              (info)=>{


                progress(
                  callback,
                  {

                    stage:
                      "download",


                    progress:
                      info.progress,


                    message:
                      info.text


                  }
                );


              }


          }


        );









      progress(
        callback,
        {

          stage:
            "ready",


          message:
            "CV assistant ready."

        }
      );








      return engine;



    })();







  try {


    return await enginePromise;


  }

  catch(error){


    enginePromise =
      null;


    engine =
      null;


    throw error;


  }


}









/*
=========================================================
UNLOAD MODEL
=========================================================
*/


export async function unloadCvChat(){


  try{


    if(
      engine &&
      typeof engine.unload === "function"
    ){

      await engine.unload();

    }


  }

  catch(error){


    console.warn(
      "Unload warning:",
      error
    );


  }



  engine =
    null;


  enginePromise =
    null;


}







/*
=========================================================
STATUS
=========================================================
*/


export function getCvChatStatus(){


  return {


    loaded:
      Boolean(engine),


    model:
      CONFIG.model,


    backend:
      "WebLLM + WebGPU",


    rag:
      "cv-rag.js"


  };


}
/*
=========================================================
TEXT HELPERS
=========================================================
*/


function cleanText(text) {


  if (!text) {

    return "";

  }


  return String(text)
    .replace(/\s+/g, " ")
    .trim();


}








/*
=========================================================
NORMALIZE RETRIEVAL RESULT
=========================================================
*/


function normalizeMatch(
  match,
  index
) {


  return {


    index:
      index + 1,


    id:
      match.id ||
      "unknown",



    title:
      cleanText(
        match.title
      ),



    source:
      cleanText(
        match.source
      ),



    text:
      cleanText(
        match.text
      ),



    score:
      Number(
        match.score || 0
      ),



    tags:
      Array.isArray(match.tags)
      ?
      match.tags
      :
      []

  };


}









/*
=========================================================
REMOVE DUPLICATES

FAQ entries often repeat project information.

Example:

"Medical Imaging Experience"
and
"Cardiac MRI Project"

contain similar text.

=========================================================
*/


function removeDuplicateEvidence(
  matches
) {


  const seen =
    new Set();



  return matches.filter(
    item => {


      const key =
        (
          item.title +
          item.text
        )
        .toLowerCase()
        .replace(/\W/g,"")
        .slice(0,180);




      if (
        seen.has(key)
      ) {

        return false;

      }



      seen.add(key);



      return true;


    }

  );


}









/*
=========================================================
EVIDENCE PRIORITY SCORE

Projects > Skills > FAQ

=========================================================
*/


function calculatePriority(
  item
) {


  const content =
    (
      item.id +
      item.title +
      item.text +
      item.tags.join(" ")
    )
    .toLowerCase();




  let priority =
    item.score;



  if(
    content.includes("project")
  ){

    priority += 0.35;

  }



  if(
    content.includes("model")
  ){

    priority += 0.20;

  }



  if(
    content.includes("skill")
  ){

    priority += 0.05;

  }



  if(
    content.includes("faq")
  ){

    priority -= 0.20;

  }



  if(
    content.includes("boundary")
  ){

    priority -= 0.30;

  }



  return priority;


}









/*
=========================================================
SELECT FINAL EVIDENCE
=========================================================
*/


function selectEvidence(
  retrievalResult
) {


  if(
    !retrievalResult ||
    !retrievalResult.matches ||
    retrievalResult.matches.length === 0
  ){

    return [];

  }







  let matches =
    retrievalResult.matches
    .map(
      normalizeMatch
    );








  /*
  Remove weak matches
  */


  const bestScore =
    matches[0]?.score || 0;



  const threshold =
    Math.max(

      CONFIG.minimumScore,

      bestScore * 0.65

    );





  matches =
    matches.filter(
      item =>
        item.score >= threshold
    );









  /*
  Remove repeated information
  */


  matches =
    removeDuplicateEvidence(
      matches
    );








  /*
  Rank evidence
  */


  matches.sort(
    (a,b)=>

      calculatePriority(b)
      -
      calculatePriority(a)

  );








  /*
  Limit context size

  Smaller context =
  better small-model answers

  */


  return matches.slice(
    0,
    CONFIG.maxSources
  );


}









/*
=========================================================
BUILD EVIDENCE TEXT
=========================================================
*/


function buildEvidenceBlock(
  evidence
) {


  return evidence
  .map(
    (item)=>{


      return `

[${item.index}]

Title:
${item.title}

Source:
${item.source}

Knowledge ID:
${item.id}

Evidence:
${item.text}

`;

    }

  )
  .join("\n");


}
/*
=========================================================
BUILD GROUNDED PROMPT
=========================================================
*/


function buildPrompt(
  question,
  retrievalResult
) {


  const evidence =
    selectEvidence(
      retrievalResult
    );



  if(
    evidence.length === 0
  ){

    return {

      hasEvidence:
        false,


      evidence:
        [],


      prompt:
        null

    };

  }







  const evidenceText =
    buildEvidenceBlock(
      evidence
    );








  const prompt = `

QUESTION:

${question}



VERIFIED CV EVIDENCE:

${ evidenceText }



INSTRUCTIONS:

Answer the question using ONLY the verified evidence.

Important:

- Evidence is already verified.
- If a project is mentioned, explain that project first.
- Mention technologies used.
- Mention results only when provided.
- Do not repeat the same information multiple times.
- Do not invent missing facts.
- Do not claim employment unless evidence says so.
- Do not claim medical deployment or clinical validation.
- Add citations using [number].



FINAL ANSWER:

`;





  return {


    hasEvidence:
      true,


    evidence,


    prompt


  };


}









/*
=========================================================
BAD ANSWER DETECTOR
=========================================================
*/


function isWeakAnswer(
  answer
) {


  if(
    !answer
  ){

    return true;

  }



  const text =
    answer.toLowerCase();




  const badPatterns = [

    "i don't know",

    "i do not know",

    "not available",

    "cannot answer",

    "can't answer",

    "no information"

  ];





  return badPatterns.some(
    pattern =>
      text.includes(pattern)
  );


}









/*
=========================================================
FALLBACK ANSWER

Used if:
- retrieval succeeded
- model ignores evidence

=========================================================
*/


function buildFallbackAnswer(
  evidence
) {


  if(
    !evidence ||
    evidence.length === 0
  ){

    return UNKNOWN;

  }




  const main =
    evidence[0];





  let answer =
`${main.title}: ${main.text}`;







  if(
    evidence.length > 1
  ){

    answer +=
      "\n\nRelated information:";



    evidence
    .slice(1)
    .forEach(
      item => {


        answer +=
`\n\n[${item.index}] ${item.title}: ${item.text}`;


      }

    );

  }




  return answer;


}









/*
=========================================================
MAIN CHAT FUNCTION
=========================================================
*/


export async function askCvAssistant(
  question,
  options = {}
) {


  const {

    onProgress =
      null

  } = options;








  if(
    !question ||
    !question.trim()
  ){

    throw new Error(
      "Question is empty."
    );

  }






  const cleanQuestion =
    question.trim();








  progress(
    onProgress,
    {

      stage:
        "retrieving",


      message:
        "Searching CV knowledge..."

    }
  );









  const retrievalResult =
    await retrieveCvContext(
      cleanQuestion
    );









  const promptData =
    buildPrompt(
      cleanQuestion,
      retrievalResult
    );








  /*
  No evidence:
  do not call LLM
  */


  if(
    !promptData.hasEvidence
  ){

    return {


      answer:
        UNKNOWN,


      sources:
        [],


      retrieval:
        retrievalResult


    };


  }









  if(
    !engine
  ){

    await initializeCvChat(
      onProgress
    );

  }








  progress(
    onProgress,
    {

      stage:
        "generating",


      message:
        "Generating answer..."

    }
  );









  const response =
    await engine.chat.completions.create({

      messages:[


        {

          role:
            "system",


          content:
            SYSTEM_PROMPT

        },


        {

          role:
            "user",


          content:
            promptData.prompt

        }


      ],



      temperature:
        CONFIG.temperature,



      top_p:
        CONFIG.topP,



      max_tokens:
        CONFIG.maxTokens


    });









  let answer =
    response
    ?.choices?.[0]
    ?.message
    ?.content
    ?.trim();









  /*
  Small local models sometimes refuse.

  Use evidence fallback.
  */


  if(
    isWeakAnswer(answer)
  ){

    answer =
      buildFallbackAnswer(
        promptData.evidence
      );

  }








  return {


    answer,


    sources:
      promptData.evidence.map(
        item => ({

          id:
            item.id,


          title:
            item.title,


          score:
            item.score

        })
      ),



    retrieval:
      retrievalResult


  };


}








/*
=========================================================
DEBUG PROMPT
=========================================================
*/


export async function debugCvChatPrompt(
  question
){


  const retrieval =
    await retrieveCvContext(
      question
    );



  return buildPrompt(
    question,
    retrieval
  );


}
/*
=========================================================
STREAMING WRAPPER
=========================================================
*/


export async function askCvAssistantStream(
  question,
  callbacks = {}
) {


  return askCvAssistant(

    question,

    {

      onProgress:
        callbacks.onProgress

    }

  );


}









/*
=========================================================
READY STATUS
=========================================================
*/


export function isCvChatReady(){

  return Boolean(
    engine
  );

}









/*
=========================================================
CONFIG DEBUG
=========================================================
*/


export function getCvChatConfig(){

  return {


    model:
      CONFIG.model,


    maxSources:
      CONFIG.maxSources,


    maxTokens:
      CONFIG.maxTokens,


    temperature:
      CONFIG.temperature


  };


}









/*
=========================================================
PIPELINE TEST

Does retrieval + prompt building
without loading WebLLM.

Useful for debugging.

Example:

await testCvPipeline(
"What experience does Arad have with medical imaging?"
)

=========================================================
*/


export async function testCvPipeline(
  question
){


  const retrieval =
    await retrieveCvContext(
      question
    );



  return {


    retrieval,


    prompt:
      buildPrompt(
        question,
        retrieval
      )


  };


}









/*
=========================================================
RESET CHAT ENGINE

Used when:
- changing model
- updating knowledge base

=========================================================
*/


export async function resetCvChat(){


  try{


    if(
      engine &&
      typeof engine.unload === "function"
    ){

      await engine.unload();

    }


  }

  catch(error){


    console.warn(
      "Unload failed:",
      error
    );


  }






  engine =
    null;



  enginePromise =
    null;



  webllmPromise =
    null;





  return {


    reset:
      true


  };


}









/*
=========================================================
DEFAULT EXPORT
=========================================================
*/


export default {


  checkCvChatSupport,


  initializeCvChat,


  askCvAssistant,


  askCvAssistantStream,


  unloadCvChat,


  resetCvChat,


  getCvChatStatus,


  getCvChatConfig,


  isCvChatReady,


  testCvPipeline,


  debugCvChatPrompt


};