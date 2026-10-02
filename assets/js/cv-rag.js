/*
=========================================================
 ARAD CV — CLIENT SIDE RAG RETRIEVAL ENGINE
=========================================================

Responsibilities:

- Load cv-knowledge-base.json
- Convert structured knowledge into RAG chunks
- Load Transformers.js lazily
- Generate embeddings
- Cache vectors in IndexedDB
- Search CV knowledge
- Apply project-aware ranking

Does NOT:
- Generate answers
- Load WebLLM
- Control UI

=========================================================
*/


/* =======================================================
   CONFIGURATION
======================================================= */


const RAG_CONFIG = Object.freeze({

  transformersUrl:
    "https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.8.1",


  knowledgeBaseUrl:
    new URL(
      "../cv/cv-knowledge-base.json",
      import.meta.url
    ).href,


  fallbackEmbeddingModel:
    "Xenova/all-MiniLM-L6-v2",


  dbName:
    "arad-cv-rag",


  dbVersion:
    1,


  storeName:
    "vector-cache",


  cacheKey:
    "cv-vectors",


  defaultTopK:
    5,


  defaultMinScore:
    0.28

});





/* =======================================================
   INTERNAL STATE
======================================================= */


let transformersModulePromise =
  null;


let embedderPromise =
  null;


let knowledgeBasePromise =
  null;


let vectorIndexPromise =
  null;






/* =======================================================
   PROGRESS EVENTS
======================================================= */


function emitProgress(
  callback,
  detail
) {

  if (
    typeof callback === "function"
  ) {

    callback(detail);

  }

}







/* =======================================================
   LOAD TRANSFORMERS.JS
======================================================= */


async function loadTransformers() {


  if (
    !transformersModulePromise
  ) {


    transformersModulePromise =
      import(
        RAG_CONFIG.transformersUrl
      );


  }


  return transformersModulePromise;


}








/* =======================================================
   NORMALIZE KNOWLEDGE BASE
=======================================================

Converts:

{
 profile:{},
 projects:[],
 skills:{},
 models:[]
}

into:

{
 version:"",
 chunks:[
   {
    id:"",
    title:"",
    text:"",
    tags:[]
   }
 ]
}

======================================================= */


function normalizeKnowledgeBase(
  data
) {


  /*
   Already old format.
  */

  if (
    Array.isArray(
      data.chunks
    )
  ) {

    return data;

  }





  const chunks = [];






  /*
  -------------------------
  PROFILE
  -------------------------
  */


  if (
    data.profile
  ) {


    chunks.push({

      id:
        "profile",


      title:
        "Professional Profile",


      text:
        JSON.stringify(
          data.profile,
          null,
          2
        ),


      tags:
        [
          "profile",
          "bio"
        ],


      source:
        "Knowledge CV"


    });


  }









  /*
  -------------------------
  SUMMARY
  -------------------------
  */


  if (
    data.professional_summary
  ) {


    chunks.push({

      id:
        "professional-summary",


      title:
        "Professional Summary",


      text:
        JSON.stringify(
          data.professional_summary,
          null,
          2
        ),


      tags:
        [
          "summary",
          "profile"
        ],


      source:
        "Knowledge CV"


    });


  }








  /*
  -------------------------
  PROJECTS
  -------------------------
  */


  if (
    Array.isArray(
      data.projects
    )
  ) {


    data.projects.forEach(
      project => {


        chunks.push({

          id:
            `project-${project.id}`,


          title:
            project.title,


          text:
            [

              project.description || "",


              ...(project.details || []),


              "Technologies:",


              ...(project.technologies || []),


              "Categories:",


              ...(project.category || [])


            ]
            .join("\n"),



          tags:
            [
              "project",

              ...(project.category || []),

              ...(project.technologies || [])
            ],



          source:
            project.source ||
            "Portfolio"


        });


      }
    );


  }








  /*
  -------------------------
  MODELS
  -------------------------
  */


  if (
    Array.isArray(
      data.models
    )
  ) {


    data.models.forEach(
      model => {


        chunks.push({

          id:
            `model-${model.id || model.name}`,


          title:
            model.name ||
            model.title ||
            "AI Model",


          text:
            JSON.stringify(
              model,
              null,
              2
            ),


          tags:
            [
              "model",
              "machine learning",
              "AI"
            ],


          source:
            "Knowledge CV"


        });


      }
    );


  }








  /*
  -------------------------
  DATASETS
  -------------------------
  */


  if (
    Array.isArray(
      data.datasets
    )
  ) {


    data.datasets.forEach(
      dataset => {


        chunks.push({

          id:
            `dataset-${dataset.id || dataset.name}`,


          title:
            dataset.name ||
            dataset.title ||
            "Dataset",


          text:
            JSON.stringify(
              dataset,
              null,
              2
            ),


          tags:
            [
              "dataset",
              "data"
            ],


          source:
            "Knowledge CV"


        });


      }
    );


  }









  /*
  -------------------------
  SKILLS
  -------------------------
  */


  if (
    data.skills
  ) {


    Object.entries(
      data.skills
    )
    .forEach(
      (
        [
          category,
          skills
        ]
      ) => {


        chunks.push({

          id:
            `skills-${category}`,


          title:
            category,


          text:
            Array.isArray(skills)

              ?

                skills.join(", ")

              :

                JSON.stringify(
                  skills,
                  null,
                  2
                ),


          tags:
            [
              "skills",
              category
            ],


          source:
            "Knowledge CV"


        });


      }
    );


  }








  /*
  -------------------------
  TOOLS
  -------------------------
  */


  if (
    data.tools_and_frameworks
  ) {


    chunks.push({

      id:
        "tools-frameworks",


      title:
        "Tools and Frameworks",


      text:
        JSON.stringify(
          data.tools_and_frameworks,
          null,
          2
        ),


      tags:
        [
          "tools",
          "frameworks"
        ],


      source:
        "Knowledge CV"


    });


  }







  /*
  -------------------------
  FAQ
  -------------------------
  */


  if (
    Array.isArray(
      data.faq
    )
  ) {


    data.faq.forEach(
      item => {


        chunks.push({

          id:
            `faq-${item.id || item.question}`,


          title:
            item.question,


          text:
            item.answer,


          tags:
            [
              "faq"
            ],


          source:
            "Knowledge CV"


        });


      }
    );


  }






  return {


    version:
      data.knowledgeVersion ||
      "unknown",



    embedding_model:
      data.embedding_model ||
      "Xenova/all-MiniLM-L6-v2",



    chunks


  };


}







/* =======================================================
   LOAD KNOWLEDGE BASE
======================================================= */


async function loadKnowledgeBase() {


  if (
    !knowledgeBasePromise
  ) {


    knowledgeBasePromise =
      fetch(
        RAG_CONFIG.knowledgeBaseUrl,

        {

          cache:
            "no-cache",


          headers:
            {

              Accept:
                "application/json"

            }

        }

      )

      .then(
        async response => {


          if (
            !response.ok
          ) {


            throw new Error(
              `Could not load CV knowledge base (${response.status}).`
            );


          }





          const rawData =
            await response.json();





          const data =
            normalizeKnowledgeBase(
              rawData
            );





          if (
            !data ||
            !Array.isArray(
              data.chunks
            ) ||
            data.chunks.length === 0
          ) {


            throw new Error(
              "CV knowledge base has no searchable chunks."
            );


          }





          return data;


        }

      )

      .catch(
        error => {


          knowledgeBasePromise =
            null;


          throw error;


        }

      );


  }


  return knowledgeBasePromise;


}
/* =======================================================
   INDEXEDDB HELPERS
======================================================= */


function openDatabase() {


  return new Promise(
    (
      resolve,
      reject
    ) => {


      const request =
        indexedDB.open(

          RAG_CONFIG.dbName,

          RAG_CONFIG.dbVersion

        );




      request.onupgradeneeded =
        event => {


          const db =
            event.target.result;



          if (
            !db.objectStoreNames.contains(
              RAG_CONFIG.storeName
            )
          ) {


            db.createObjectStore(
              RAG_CONFIG.storeName
            );

          }


        };





      request.onsuccess =
        () => {


          resolve(
            request.result
          );


        };





      request.onerror =
        () => {


          reject(
            request.error
          );


        };


    }

  );


}








async function readCache(
  key
) {


  try {


    const db =
      await openDatabase();




    return await new Promise(
      (
        resolve,
        reject
      ) => {


        const transaction =
          db.transaction(
            RAG_CONFIG.storeName,
            "readonly"
          );



        const store =
          transaction.objectStore(
            RAG_CONFIG.storeName
          );



        const request =
          store.get(
            key
          );



        request.onsuccess =
          () => {


            resolve(
              request.result || null
            );


          };




        request.onerror =
          () => {


            reject(
              request.error
            );


          };


      }

    );


  }

  catch(error) {


    console.warn(
      "IndexedDB read failed",
      error
    );


    return null;


  }


}








async function writeCache(
  key,
  value
) {


  try {


    const db =
      await openDatabase();




    return await new Promise(
      (
        resolve,
        reject
      ) => {


        const transaction =
          db.transaction(
            RAG_CONFIG.storeName,
            "readwrite"
          );



        const store =
          transaction.objectStore(
            RAG_CONFIG.storeName
          );



        const request =
          store.put(
            value,
            key
          );



        request.onsuccess =
          () => {


            resolve(
              true
            );


          };



        request.onerror =
          () => {


            reject(
              request.error
            );


          };


      }

    );


  }

  catch(error) {


    console.warn(
      "IndexedDB write failed",
      error
    );


    return false;


  }


}








export async function clearCvRagCache() {


  try {


    const db =
      await openDatabase();




    await new Promise(
      (
        resolve,
        reject
      ) => {


        const transaction =
          db.transaction(
            RAG_CONFIG.storeName,
            "readwrite"
          );



        const store =
          transaction.objectStore(
            RAG_CONFIG.storeName
          );



        const request =
          store.clear();




        request.onsuccess =
          resolve;



        request.onerror =
          reject;



      }

    );



    console.log(
      "CV RAG cache cleared"
    );


  }

  catch(error) {


    console.warn(
      error
    );


  }


}








/* =======================================================
   LOAD EMBEDDING MODEL
======================================================= */


async function loadEmbeddingModel(
  onProgress
) {


  if (
    embedderPromise
  ) {


    return embedderPromise;


  }






  embedderPromise =
    (async () => {



      emitProgress(
        onProgress,
        {

          stage:
            "embedding-model",


          message:
            "Loading embedding model..."

        }
      );






      const transformers =
        await loadTransformers();






      const {

        pipeline

      } =
        transformers;







      const extractor =
        await pipeline(

          "feature-extraction",

          RAG_CONFIG.fallbackEmbeddingModel,

          {

            dtype:
              "fp32",


            progress_callback:
              progress => {


                emitProgress(
                  onProgress,
                  {

                    stage:
                      "embedding-download",


                    progress

                  }
                );


              }

          }

        );







      return extractor;



    })()

    .catch(
      error => {


        embedderPromise =
          null;


        throw error;


      }

    );






  return embedderPromise;


}








/* =======================================================
   TEXT EMBEDDING
======================================================= */


async function createEmbedding(
  text,
  extractor
) {


  const output =
    await extractor(

      text,

      {

        pooling:
          "mean",


        normalize:
          true

      }

    );





  return Array.from(
    output.data
  );


}








/* =======================================================
   CREATE VECTOR INDEX
======================================================= */


async function buildVectorIndex(
  knowledgeBase,
  onProgress
) {



  const cached =
    await readCache(
      RAG_CONFIG.cacheKey
    );







  if (
    cached &&

    cached.version ===
      knowledgeBase.version &&

    cached.chunks?.length ===
      knowledgeBase.chunks.length
  ) {


    emitProgress(
      onProgress,
      {

        stage:
          "cache",

        message:
          "Using cached CV embeddings."

      }
    );



    return cached;


  }







  const extractor =
    await loadEmbeddingModel(
      onProgress
    );







  const vectors =
    [];







  for (
    let i = 0;

    i <
    knowledgeBase.chunks.length;

    i++

  ) {



    const chunk =
      knowledgeBase.chunks[i];





    emitProgress(
      onProgress,
      {

        stage:
          "embedding",


        current:
          i + 1,


        total:
          knowledgeBase.chunks.length,


        message:
          `Embedding ${chunk.title}`

      }
    );






    const text =
      [

        chunk.title,

        chunk.text,

        (chunk.tags || []).join(
          " "
        )

      ]

      .join(
        "\n"
      );







    vectors.push({

      ...chunk,


      vector:
        await createEmbedding(
          text,
          extractor
        )


    });



  }







  const index =
    {


      version:
        knowledgeBase.version,



      embeddingModel:
        RAG_CONFIG.fallbackEmbeddingModel,



      chunks:
        vectors



    };








  await writeCache(
    RAG_CONFIG.cacheKey,
    index
  );







  return index;



}







/* =======================================================
   VECTOR MATH
======================================================= */


function cosineSimilarity(
  a,
  b
) {


  let dot =
    0;


  let normA =
    0;


  let normB =
    0;





  const length =
    Math.min(
      a.length,
      b.length
    );






  for (
    let i = 0;

    i < length;

    i++

  ) {


    dot +=
      a[i] *
      b[i];


    normA +=
      a[i] *
      a[i];


    normB +=
      b[i] *
      b[i];


  }






  if (
    normA === 0 ||
    normB === 0
  ) {


    return 0;


  }







  return (
    dot /
    (
      Math.sqrt(normA) *
      Math.sqrt(normB)
    )
  );


}
/* =======================================================
   QUERY EXPANSION
======================================================= */


function expandQuery(
  query
) {


  const lower =
    query
      .toLowerCase();



  const expansions =
    [];





  if (
    lower.includes(
      "medical"
    )
    ||
    lower.includes(
      "mri"
    )
    ||
    lower.includes(
      "imaging"
    )
    ||
    lower.includes(
      "health"
    )
  ) {


    expansions.push(

      "medical imaging MRI segmentation MONAI 3D U-Net NIfTI computer vision"

    );


  }







  if (
    lower.includes(
      "qlora"
    )
    ||
    lower.includes(
      "fine tuning"
    )
    ||
    lower.includes(
      "finetuning"
    )
  ) {


    expansions.push(

      "QLoRA LoRA PEFT quantization fine-tuning transformers Hugging Face"

    );


  }







  if (
    lower.includes(
      "rag"
    )
    ||
    lower.includes(
      "retrieval"
    )
    ||
    lower.includes(
      "chatbot"
    )
  ) {


    expansions.push(

      "RAG embeddings vector database semantic search LangChain"

    );


  }







  if (
    lower.includes(
      "llm"
    )
    ||
    lower.includes(
      "language model"
    )
    ||
    lower.includes(
      "gpt"
    )
  ) {


    expansions.push(

      "large language model transformer NLP generative AI"

    );


  }








  if (
    lower.includes(
      "project"
    )
    ||
    lower.includes(
      "built"
    )
    ||
    lower.includes(
      "developed"
    )
  ) {


    expansions.push(

      "project implementation development architecture"

    );


  }







  return [

    query,

    ...expansions

  ]

  .join(
    " "
  );

}





/* =======================================================
   QUESTION TYPE DETECTION
======================================================= */


function detectQuestionType(
  query
) {


  const q =
    query
      .toLowerCase();




  if (

    q.includes(
      "experience"
    )

    ||

    q.includes(
      "project"
    )

    ||

    q.includes(
      "built"
    )

    ||

    q.includes(
      "developed"
    )

  ) {


    return "experience";


  }







  if (

    q.includes(
      "skill"
    )

    ||

    q.includes(
      "know"
    )

    ||

    q.includes(
      "technology"
    )

  ) {


    return "skill";


  }







  if (

    q.includes(
      "model"
    )

    ||

    q.includes(
      "trained"
    )

  ) {


    return "model";


  }







  return "general";


}








/* =======================================================
   KNOWLEDGE TYPE BOOSTING
======================================================= */


function getKnowledgeBoost(
  chunk,
  questionType
) {


  const tags =
    (chunk.tags || [])
      .map(
        tag =>
          String(tag)
            .toLowerCase()
      );




  let boost =
    0;






  /*
    Project answers are preferred
    for experience questions.
  */


  if (
    questionType === "experience"
    &&
    tags.includes(
      "project"
    )
  ) {


    boost +=
      0.35;


  }






  /*
    Models for model questions.
  */


  if (
    questionType === "model"
    &&
    tags.includes(
      "model"
    )
  ) {


    boost +=
      0.35;


  }







  /*
    Skills support but don't dominate.
  */


  if (
    tags.includes(
      "skills"
    )
  ) {


    boost +=
      0.12;


  }







  /*
    FAQ entries are useful.
  */


  if (
    tags.includes(
      "faq"
    )
  ) {


    boost +=
      0.20;


  }







  /*
    Medical project priority.
  */


  if (

    tags.some(
      tag =>
        [
          "medical imaging",
          "medical ai",
          "mri",
          "computer vision"
        ]
        .includes(tag)
    )

  ) {


    boost +=
      0.10;


  }






  return boost;


}








/* =======================================================
   KEYWORD SCORE
======================================================= */


function keywordScore(
  query,
  chunk
) {


  const words =
    query
      .toLowerCase()
      .split(
        /\s+/
      )
      .filter(
        word =>
          word.length > 2
      );




  const searchable =
    [

      chunk.title,

      chunk.text,

      ...(chunk.tags || [])

    ]

    .join(
      " "
    )

    .toLowerCase();






  let matches =
    0;






  words.forEach(
    word => {


      if (
        searchable.includes(
          word
        )
      ) {


        matches++;

      }


    }

  );







  if (
    words.length === 0
  ) {


    return 0;


  }







  return (
    matches /
    words.length
  );


}







/* =======================================================
   RERANK RESULTS
======================================================= */


function rerankResults(
  results,
  query
) {


  const questionType =
    detectQuestionType(
      query
    );





  return results

    .map(
      item => {


        const boost =
          getKnowledgeBoost(
            item,
            questionType
          );



        const keyword =
          keywordScore(
            query,
            item
          );





        return {


          ...item,


          semanticScore:
            item.score,



          rerankBoost:
            boost,



          keywordScore:
            keyword,



          score:
            item.score
            +
            boost
            +
            (
              keyword *
              0.20
            )


        };


      }

    )


    .sort(
      (
        a,
        b
      ) =>
        b.score -
        a.score
    );


}







/* =======================================================
   CREATE QUERY EMBEDDING
======================================================= */


async function embedQuery(
  query
) {


  const extractor =
    await loadEmbeddingModel();




  return createEmbedding(

    expandQuery(
      query
    ),

    extractor

  );


}
/* =======================================================
   INITIALIZE CV RAG
======================================================= */


export async function initializeCvRag(
  {
    onProgress
  } = {}
) {


  if (
    vectorIndexPromise
  ) {


    return vectorIndexPromise;


  }







  vectorIndexPromise =
    (async () => {



      emitProgress(
        onProgress,
        {

          stage:
            "knowledge",


          message:
            "Loading CV knowledge base..."

        }
      );








      const knowledgeBase =
        await loadKnowledgeBase();







      const index =
        await buildVectorIndex(

          knowledgeBase,

          onProgress

        );







      emitProgress(
        onProgress,
        {

          stage:
            "ready",


          message:
            "CV retrieval system ready.",


          chunkCount:
            index.chunks.length

        }
      );







      return {


        knowledgeVersion:
          knowledgeBase.version,


        embeddingModel:
          index.embeddingModel,


        chunkCount:
          index.chunks.length,


        index


      };





    })()

    .catch(
      error => {


        vectorIndexPromise =
          null;


        throw error;


      }

    );







  return vectorIndexPromise;


}









/* =======================================================
   RETRIEVE CONTEXT
======================================================= */


export async function retrieveCvContext(
  query,

  {
    topK =
      RAG_CONFIG.defaultTopK,


    minScore =
      RAG_CONFIG.defaultMinScore,


    onProgress

  } = {}

) {



  const cleanQuery =
    String(
      query || ""
    )
    .trim();







  if (
    !cleanQuery
  ) {


    return {


      question:
        "",


      hasRelevantContext:
        false,


      matches:
        []


    };


  }








  const rag =
    await initializeCvRag(
      {
        onProgress
      }
    );







  emitProgress(
    onProgress,
    {

      stage:
        "search",


      message:
        "Searching CV knowledge..."

    }
  );







  const queryVector =
    await embedQuery(
      cleanQuery
    );








  const candidates =
    rag.index.chunks

      .map(
        chunk => {


          return {


            ...chunk,


            score:
              cosineSimilarity(

                queryVector,

                chunk.vector

              )


          };


        }

      )



      .filter(
        item =>
          item.score >= minScore
      );









  const ranked =
    rerankResults(

      candidates,

      cleanQuery

    );









  const matches =
    ranked

      .slice(
        0,
        topK
      )

      .map(
        item => {


          const {

            vector,

            ...cleanItem

          } =
            item;






          return cleanItem;


        }

      );








  return {


    question:
      cleanQuery,



    expandedQuestion:
      expandQuery(
        cleanQuery
      ),



    knowledgeVersion:
      rag.knowledgeVersion,



    embeddingModel:
      rag.embeddingModel,



    threshold:
      minScore,



    hasRelevantContext:
      matches.length > 0,



    bestScore:
      matches[0]?.score || 0,



    matches



  };


}









/* =======================================================
   GET KNOWLEDGE STATUS
======================================================= */


export async function getCvRagStatus() {


  try {


    const knowledge =
      await loadKnowledgeBase();



    return {


      knowledgeVersion:
        knowledge.version,



      chunkCount:
        knowledge.chunks.length,



      embeddingModel:
        RAG_CONFIG.fallbackEmbeddingModel


    };


  }

  catch(error) {


    return {


      error:
        error.message


    };


  }


}









/* =======================================================
   CONFIG EXPORT
======================================================= */


export const cvRagConfig =
  RAG_CONFIG;