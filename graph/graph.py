from graph.node_constants import RETRIEVE, GRADE_DOCUMENTS, GENERATE, WEBSEARCH
from graph.nodes import generate, grade_documents, retrieve, web_search
from graph.state import GraphState
from graph.chains.router import question_router,RouteQuery
from graph.chains.hallucination_grader import hallucination_grader
from graph.chains.answer_grader import answer_grader
from langgraph.graph import END,StateGraph

from dotenv import load_dotenv

load_dotenv()

def decide_to_generate(state:GraphState):
    print("---ASSESS GRADED DOCUMENTS---")
    if state["web_search"]:
        print("----WEBSEARCH----")
        return WEBSEARCH
    else:
        return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("---CHECK HALLUCINATIONS---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if hallucination_grade := score.binary_score:
        print("---DECISION: GENERATION IS GROUNDED IN DOCUMENTS---")
        print("---GRADE GENERATION vs QUESTION---")
        score = answer_grader.invoke({"question": question, "generation": generation})
        if answer_grade := score.binary_score:
            print("---DECISION: GENERATION ADDRESSES QUESTION---")
            return "useful"
        else:
            print("---DECISION: GENERATION DOES NOT ADDRESS QUESTION---")
            return "not useful"
    else:
        print("---DECISION: GENERATION IS NOT GROUNDED IN DOCUMENTS, RE-TRY---")
        return "not supported"


def route_question(state: GraphState) -> str:
    question = state.get("question")
    source = state.get("source", {})  # Default empty dict

    # Dict erişimi için [] veya get() kullan
    if source.get("datasource") == WEBSEARCH:
        return WEBSEARCH

    # Default olarak RETRIEVE'e yönlendir
    return RETRIEVE



workflow = StateGraph(GraphState)

workflow.add_node(RETRIEVE,retrieve)
workflow.add_node(GENERATE,generate)
workflow.add_node(WEBSEARCH,web_search)
workflow.add_node(GRADE_DOCUMENTS,grade_documents)

workflow.set_conditional_entry_point(
    route_question,
    path_map={RETRIEVE:RETRIEVE,WEBSEARCH:WEBSEARCH}
)

workflow.add_edge(RETRIEVE,GRADE_DOCUMENTS)

workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    path_map={WEBSEARCH:WEBSEARCH,GENERATE:GENERATE}
)

workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    path_map={"useful": END, "not useful": WEBSEARCH,"not supported": GENERATE}
)

workflow.add_edge(WEBSEARCH,GENERATE)
workflow.add_edge(GENERATE,END)



app = workflow.compile()
app.get_graph().draw_mermaid_png(output_file_path="graph.png")